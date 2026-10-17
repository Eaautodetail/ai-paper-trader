"""Historical comparison of candidate strategies with an in-sample / out-of-sample split.

Uses the exact same SessionEngine, RiskManager and cost model as live paper trading,
on real 1-minute Yahoo bars, starting from 500 SEK. Strategy variants are ranked on the
earlier (in-sample) days only; the later (out-of-sample) days are reported separately and
never used for selection. Nothing here is a promise of future results.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from . import data as md
from .costs import CostModel
from .engine import SessionEngine
from .features import compute_features
from .ledger import Ledger
from .market_calendar import MarketCalendar
from .risk import RiskManager
from .strategies import Strategy, candidate_grid


def day_frames(bars: dict[str, pd.DataFrame], cal: MarketCalendar, d) -> tuple:
    w = cal.window(d)
    if w is None:
        return None, {}
    lo, hi = pd.Timestamp(w.open), pd.Timestamp(w.end) + pd.Timedelta(minutes=10)
    frames = {}
    for s, df in bars.items():
        day = df[(df.index >= lo) & (df.index <= hi)]
        if len(day) >= 30:
            frames[s] = compute_features(day, w.open)
    return w, frames


def run_strategy(strategy: Strategy, days: list, prepared: dict, cfg: dict, start_usd: float, fx: float) -> dict:
    """Runs one strategy over the given days, starting from start_usd, compounding day to day."""
    costs = CostModel(cfg)
    risk = RiskManager(cfg, costs)
    led = Ledger(":memory:")
    led.quiet = True
    led.db.execute("INSERT INTO account VALUES (1, ?, ?, 0, ?, ?, '', ?)",
                   (start_usd * fx, fx, start_usd, start_usd, json.dumps(strategy.describe())))
    daily = []
    for d in days:
        w, frames, liq, market = prepared[d]
        if w is None or not frames:
            continue
        eq0 = led.cash()
        universe = md.select_universe(liq, cfg, eq0, costs) if not liq.empty else []
        frames = {s: f for s, f in frames.items() if s in universe}
        led.start_session(d.isoformat(), "backtest", eq0, fx, universe)
        eng = SessionEngine(led, w, strategy, costs, risk, "backtest", fx_usdsek=fx)
        eng.process(frames, market=market)
        if not eng.flat():
            eng.finalize_without_bars(pd.Timestamp(w.end))
        eq1 = led.cash()
        led.mark_session(d.isoformat(), "backtest", "completed", end_equity_usd=eq1)
        daily.append({"day": d.isoformat(), "start": eq0, "end": eq1, "pnl": eq1 - eq0, "universe": len(universe)})
    trades = [dict(t) for t in led.trades()]
    rej = [e["message"] for e in led.events() if e["level"] == "SKIP"]
    led.close()
    return {"daily": daily, "trades": trades, "rejections": rej}


def metrics(res: dict, start_usd: float) -> dict:
    daily = pd.DataFrame(res["daily"])
    trades = pd.DataFrame(res["trades"])
    if daily.empty:
        return {"days": 0}
    eq = np.concatenate([[daily["start"].iloc[0]], daily["end"].to_numpy()])
    dd = float(((eq - np.maximum.accumulate(eq)) / np.maximum.accumulate(eq)).min())
    n = len(trades)
    net = float(daily["pnl"].sum())
    wins = trades[trades["net_pnl"] > 0] if n else trades
    losses = trades[trades["net_pnl"] <= 0] if n else trades
    pf = float(wins["net_pnl"].sum() / -losses["net_pnl"].sum()) if n and losses["net_pnl"].sum() < 0 else None
    return {
        "days": int(len(daily)), "trades": int(n),
        "net_pnl_usd": round(net, 4), "return_pct": round(100 * net / daily["start"].iloc[0], 3),
        "win_rate_pct": round(100 * len(wins) / n, 1) if n else None,
        "avg_net_per_trade_usd": round(net / n, 4) if n else None,
        "modeled_costs_usd": round(float(trades["costs"].sum()), 4) if n else 0.0,
        "gross_before_costs_usd": round(float((trades["net_pnl"] + trades["costs"]).sum()), 4) if n else 0.0,
        "max_drawdown_pct": round(100 * dd, 3), "profit_factor": round(pf, 3) if pf else None,
        "positive_days": int((daily["pnl"] > 0).sum()), "avg_universe": round(float(daily["universe"].mean()), 1),
    }


def load_history(cfg: dict, root: Path | None = None, days_back: int = 29) -> dict:
    """Real 1-minute bars: everything in the local archive plus Yahoo's last ~30 days."""
    from . import archive
    cal = MarketCalendar(cfg)
    tz = cal.tz
    bench = cfg["universe"]["benchmark"]
    syms = cfg["universe"]["symbols"] + [bench]
    end = datetime.now(tz)
    start = end - timedelta(days=days_back)
    print(f"Downloading 1-minute bars {start:%Y-%m-%d}..{end:%Y-%m-%d} for {len(syms)} symbols", flush=True)
    bars = md.intraday_range(syms, tz, start, end + timedelta(days=1))
    if root is not None:
        stored = archive.load(root, tz)
        if stored:
            print(f"Adding archived bars for {len({d for df in stored.values() for d in df.index.date})} days", flush=True)
            bars = archive.merge(stored, bars)
    daily_bars = md.daily(syms, tz, period="1y")
    fx = md.usdsek(cfg["universe"]["fx_symbol"])
    days = sorted({d for df in bars.values() for d in df.index.date if cal.is_trading_day(d) and d < end.date()})
    prepared = {}
    for d in days:
        w, frames = day_frames(bars, cal, d)
        market = frames.pop(bench, None)
        prepared[d] = (w, frames, md.liquidity_table(daily_bars, pd.Timestamp(d)), market)
    days = [d for d in days if prepared[d][1]]
    return {"days": days, "prepared": prepared, "fx": fx}


def evaluate(cfg: dict, hist: dict, strategies: list, oos_fraction: float = 1 / 3, start_usd: float | None = None) -> tuple:
    days, prepared, fx = hist["days"], hist["prepared"], hist["fx"]
    if start_usd is None:
        start_usd = cfg["capital"]["initial_sek"] * (1 - cfg["capital"]["fx_conversion_fee_pct"] / 100) / fx
    n_oos = max(1, round(len(days) * oos_fraction))
    ins, oos = days[:-n_oos], days[-n_oos:]
    print(f"{len(days)} trading days with data: {len(ins)} in-sample, {len(oos)} out-of-sample", flush=True)
    rows = []
    for strat in strategies:
        r_in = run_strategy(strat, ins, prepared, cfg, start_usd, fx)
        r_out = run_strategy(strat, oos, prepared, cfg, start_usd, fx)
        m_in, m_out = metrics(r_in, start_usd), metrics(r_out, start_usd)
        top_rej = pd.Series([m.split("rejected: ")[-1].split(" (")[0][:60] for m in r_in["rejections"] + r_out["rejections"]]).value_counts().head(3).to_dict()
        rows.append({"strategy": strat.describe(), "in_sample": m_in, "out_of_sample": m_out, "top_rejections": top_rej})
        print(f"{strat.name} {strat.params}: IS {m_in.get('net_pnl_usd')} USD/{m_in.get('trades')} tr | OOS {m_out.get('net_pnl_usd')} USD/{m_out.get('trades')} tr", flush=True)
    return rows, ins, oos, start_usd


def run(cfg: dict, out_dir: Path, days_back: int = 29, oos_fraction: float = 1 / 3,
        strategies: list | None = None, tag: str = "backtest", root: Path | None = None) -> dict:
    tz = MarketCalendar(cfg).tz
    hist = load_history(cfg, root, days_back)
    days, fx = hist["days"], hist["fx"]
    rows, ins, oos, start_usd = evaluate(cfg, hist, strategies or candidate_grid(), oos_fraction)

    # Selection uses in-sample results only. Requires a minimum number of trades.
    eligible = [r for r in rows if r["strategy"]["name"] != "no_trade" and r["in_sample"].get("trades", 0) >= 5]
    best = max(eligible, key=lambda r: r["in_sample"]["net_pnl_usd"]) if eligible else None
    selection = {
        "selected_at": datetime.now(tz).isoformat(timespec="seconds"),
        "data": {"source": "Yahoo Finance 1-minute bars via yfinance", "first_day": str(days[0]) if days else None,
                 "last_day": str(days[-1]) if days else None, "in_sample_days": [str(d) for d in ins],
                 "out_of_sample_days": [str(d) for d in oos], "usdsek": fx, "start_usd": start_usd},
        "rule": "Highest in-sample net P&L after all modeled costs among variants with >= 5 in-sample trades; "
                "out-of-sample days are reported but not used for the choice.",
    }
    if best:
        validated = best["in_sample"]["net_pnl_usd"] > 0 and best["out_of_sample"].get("net_pnl_usd", 0) > 0
        selection.update({"strategy": best["strategy"], "in_sample": best["in_sample"],
                          "out_of_sample": best["out_of_sample"], "validated_out_of_sample": validated})
    else:
        selection.update({"strategy": {"name": "no_trade", "params": {}}, "validated_out_of_sample": False,
                          "note": "No candidate traded enough to evaluate."})
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{tag}_results.json").write_text(json.dumps(rows, indent=1))
    write_markdown(out_dir / f"{tag}.md", rows, selection)
    return selection


def write_markdown(path: Path, rows: list, sel: dict) -> None:
    def fmt(m, k):
        v = m.get(k)
        return "-" if v is None else f"{v}"
    lines = ["# Strategy backtest", "",
             "Real 1-minute Yahoo bars, same simulator, risk limits and costs as paper trading, starting from 500 SEK.",
             "Only 09:30-11:30 New York time is traded. **This is a short sample and is not evidence of a profitable edge.**",
             "If 'move before costs' is negative, the strategy lost before any fees, so a bigger trade size would only lose more.", "",
             f"* Data: {sel['data']['first_day']} to {sel['data']['last_day']}; "
             f"in-sample {len(sel['data']['in_sample_days'])} days, out-of-sample {len(sel['data']['out_of_sample_days'])} days",
             f"* USD/SEK used: {sel['data']['usdsek']:.4f}; starting cash {sel['data']['start_usd']:.2f} USD after conversion fee",
             f"* Selection rule: {sel['rule']}",
             f"* **Selected: `{sel['strategy']['name']}` {json.dumps(sel['strategy']['params'])}**",
             f"* Out-of-sample check passed: **{'yes' if sel.get('validated_out_of_sample') else 'no'}**", "",
             "| Strategy | Params | IS trades | IS net USD | IS max DD % | OOS trades | OOS net USD | OOS win % | All days: move before costs USD | All days: costs USD | Most common rejections |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: -(r["in_sample"].get("net_pnl_usd") or 0)):
        i, o = r["in_sample"], r["out_of_sample"]
        rej = "; ".join(f"{k} ({v})" for k, v in r["top_rejections"].items())
        lines.append(f"| {r['strategy']['name']} | `{json.dumps(r['strategy']['params'])}` | {fmt(i,'trades')} | {fmt(i,'net_pnl_usd')} | "
                     f"{fmt(i,'max_drawdown_pct')} | {fmt(o,'trades')} | {fmt(o,'net_pnl_usd')} | {fmt(o,'win_rate_pct')} | "
                     f"{(i.get('gross_before_costs_usd') or 0) + (o.get('gross_before_costs_usd') or 0):+.4f} | "
                     f"{(i.get('modeled_costs_usd') or 0) + (o.get('modeled_costs_usd') or 0):.4f} | {rej} |")
    path.write_text("\n".join(lines) + "\n")
