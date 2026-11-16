"""Long-term investing paper account (simulated only): big tech and future-tech companies.

Separate from the day-trading account. Positions may be held for days or weeks. Once per
trading day, after the US close, the program looks at the finished daily bars:
  * buys are decided on day D's close and filled at day D+1's open (plus spread and slippage);
  * stops are checked against each day's low (a gap below the stop fills at the open);
  * a rising position's stop is raised (trailing stop); time and trend exits are sold at the next open.
The very same `step()` runs both the backtest (years of real daily bars) and the live paper
account, so live results are directly comparable with the test.

Which companies may be bought comes from strategy/watchlist.json (researched weekly).
The rules only use prices, so the backtest does not peek at today's news or numbers.

Limits (same spirit as the day-trading account, never loosened automatically):
  * at most 20% of the account in one company, at most 0.5% of the account planned loss per
    position (entry to stop, plus costs), no leverage, no short selling, no options;
  * if the account falls more than 2% in a day, no new buys that day;
  * holding overnight is allowed here (that is the point of investing), protected by the stop.
"""
import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from .costs import CostModel
from .safety import LIVE_TRADING_ENABLED, SafetyError

DEFAULT_PARAMS = {"name": "quality_dip", "dip_pct": 0.10, "rsi_max": 40, "stop_atr": 3.0, "trail_atr": 4.0,
                  "take_profit": None, "max_hold_days": 60, "trend_exit": True}


def indicators(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    c = d["Close"]
    d["sma50"] = c.rolling(50, min_periods=50).mean()
    d["sma200"] = c.rolling(200, min_periods=200).mean()
    d["high60"] = c.rolling(60, min_periods=20).max()
    d["high20_prev"] = c.shift(1).rolling(20, min_periods=20).max()
    prev = c.shift(1).fillna(d["Open"])
    tr = pd.concat([d["High"] - d["Low"], (d["High"] - prev).abs(), (d["Low"] - prev).abs()], axis=1).max(axis=1)
    d["atr"] = tr.rolling(20, min_periods=10).mean()
    delta = c.diff()
    up = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    dn = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    d["rsi"] = (100 - 100 / (1 + up / dn.replace(0, np.nan))).fillna(50)
    return d


def candidates(p: dict, rows: dict) -> list:
    """rows: symbol -> today's indicator row. Returns (score, symbol, stop_distance) best first."""
    out = []
    for s, r in rows.items():
        if any(pd.isna(r[k]) for k in ("sma200", "atr", "high60")) or r["atr"] <= 0:
            continue
        c = float(r["Close"])
        if p["name"] == "quality_dip":
            dip = 1 - c / float(r["high60"])
            if c > r["sma200"] and dip >= p["dip_pct"] and r["rsi"] <= p["rsi_max"]:
                out.append((dip, s, p["stop_atr"] * float(r["atr"])))
        elif p["name"] == "trend_breakout":
            if pd.isna(r["high20_prev"]) or pd.isna(r["sma50"]):
                continue
            if c > r["high20_prev"] and c > r["sma50"] > r["sma200"]:
                out.append((c / float(r["sma200"]) - 1, s, p["stop_atr"] * float(r["atr"])))
        elif p["name"] == "buy_hold":
            out.append((1.0, s, c * 0.99))   # benchmark only: never stopped (stop near zero)
    return sorted(out, reverse=True)


class Account:
    """The whole account state as plain JSON (cash in USD, positions, pending orders, history)."""

    def __init__(self, state: dict):
        self.s = state

    @classmethod
    def new(cls, initial_sek: float, fx: float, fx_fee_pct: float, params: dict, start_day: str) -> "Account":
        usd = initial_sek * (1 - fx_fee_pct / 100) / fx
        return cls({"initial_sek": initial_sek, "fx_initial": fx, "initial_usd": usd, "cash": usd,
                    "params": params, "start_day": start_day, "last_day": None, "positions": {},
                    "orders": [], "trades": [], "equity": [], "events": []})

    def log(self, day, msg):
        self.s["events"].append(f"{day} {msg}")

    def equity(self, closes: dict) -> float:
        return self.s["cash"] + sum(p["qty"] * closes.get(s, p["last"]) for s, p in self.s["positions"].items())


def _qty(x: float, fractional: bool) -> float:
    return math.floor(x * 1e4) / 1e4 if fractional else float(math.floor(x))


def _sell(acc: Account, costs: CostModel, day, s: str, price: float, kind: str) -> None:
    p = acc.s["positions"].pop(s)
    fees = costs.sell_fees(p["qty"], price)
    proceeds = p["qty"] * price - fees
    acc.s["cash"] += proceeds
    cost_basis = p["qty"] * p["entry"]
    acc.s["trades"].append({"symbol": s, "qty": p["qty"], "entry_day": p["entry_day"], "entry": p["entry"],
                            "exit_day": day, "exit": round(price, 4), "exit_kind": kind,
                            "net": round(proceeds - cost_basis, 4), "fees": round(fees, 4),
                            "days": p["days"]})
    acc.log(day, f"SELL {p['qty']:g} {s} @ {price:.2f} ({kind}), net {proceeds - cost_basis:+.2f} USD")


def by_day(bars: dict) -> dict:
    """symbol -> frame  becomes  date -> {symbol: that day's row} (built once, for speed)."""
    out: dict = {}
    for s, f in bars.items():
        for ts, r in zip(f.index, f.itertuples(index=False)):
            out.setdefault(ts.date(), {})[s] = r._asdict()
    return out


def step(acc: Account, day, rows: dict, costs: CostModel, cfg: dict) -> None:
    """Processes one finished trading day. rows: symbol -> that day's bar and indicators
    (computed only from that day and earlier)."""
    if LIVE_TRADING_ENABLED:
        raise SafetyError("live trading flag set")
    inv = cfg["invest"]
    p = acc.s["params"]
    frac = bool(inv.get("fractional_shares", True))
    if not rows:
        return
    closes_before = {s: pp["last"] for s, pp in acc.s["positions"].items()}
    eq_start = acc.equity(closes_before)

    # 1) Orders placed yesterday fill at today's open.
    pending, acc.s["orders"] = acc.s["orders"], []
    for o in pending:
        r = rows.get(o["symbol"])
        if r is None:
            acc.s["orders"].append(o)        # no bar today (halted?): keep the order one more day
            continue
        if o["side"] == "sell":
            if o["symbol"] in acc.s["positions"]:
                _sell(acc, costs, day, o["symbol"], costs.sell_price(float(r["Open"])), o["reason"])
            continue
        px = costs.buy_price(float(r["Open"]))
        qty = min(o["qty"], _qty(acc.s["cash"] / px, frac))
        if qty * px < inv.get("min_order_usd", 1.0) or o["symbol"] in acc.s["positions"]:
            acc.log(day, f"SKIP buy {o['symbol']}: not enough cash or already held")
            continue
        acc.s["cash"] -= qty * px
        stop = px - o["stop_dist"]
        acc.s["positions"][o["symbol"]] = {"qty": qty, "entry": round(px, 4), "entry_day": str(day), "stop": stop,
                                           "high": float(r["Open"]), "last": float(r["Close"]), "days": 0,
                                           "spread_in": round(qty * (px - float(r["Open"])), 4)}
        acc.log(day, f"BUY {qty:g} {o['symbol']} @ {px:.2f}, stop {stop:.2f} ({o['reason']})")

    # 2) Stops during the day (a gap below the stop sells at the open).
    for s in list(acc.s["positions"]):
        pos, r = acc.s["positions"][s], rows.get(s)
        if r is None:
            continue
        if float(r["Low"]) <= pos["stop"]:
            _sell(acc, costs, day, s, costs.stop_fill(pos["stop"], float(r["Open"])), "stop")

    # 3) At the close: update trailing stops and decide exits for tomorrow's open.
    for s, pos in acc.s["positions"].items():
        r = rows.get(s)
        if r is None:
            continue
        c = float(r["Close"])
        pos["last"], pos["days"] = c, pos["days"] + 1
        pos["high"] = max(pos["high"], c)
        if p.get("trail_atr") and not pd.isna(r["atr"]):
            pos["stop"] = max(pos["stop"], pos["high"] - p["trail_atr"] * float(r["atr"]))
        why = None
        if p.get("take_profit") and c >= pos["entry"] * (1 + p["take_profit"]):
            why = "take_profit"
        elif p.get("max_hold_days") and pos["days"] >= p["max_hold_days"]:
            why = "time"
        elif p.get("trend_exit") and not pd.isna(r["sma200"]) and c < r["sma200"]:
            why = "trend_broken"
        if why:
            acc.s["orders"].append({"symbol": s, "side": "sell", "reason": why, "day": str(day)})

    closes = {s: float(r["Close"]) for s, r in rows.items()}
    eq = acc.equity(closes)
    acc.s["equity"].append({"day": str(day), "equity": round(eq, 4)})

    # 4) New buys for tomorrow's open.
    if eq < eq_start * (1 - inv.get("daily_loss_limit_pct", 2.0) / 100):
        acc.log(day, f"Account fell more than {inv.get('daily_loss_limit_pct', 2.0)}% today: no new buys")
        return
    held = set(acc.s["positions"]) | {o["symbol"] for o in acc.s["orders"]}
    room = inv.get("max_positions", 8) - len(held)
    cash = acc.s["cash"]
    for score, s, dist in candidates(p, {k: v for k, v in rows.items() if k in inv["_eligible"]}):
        if room <= 0:
            break
        if s in held:
            continue
        c = closes[s]
        est = costs.buy_price(c)
        per_share_risk = dist + (est - c) + (c - costs.sell_price(c))
        risk_usd = eq * inv.get("max_risk_per_position_pct", 0.5) / 100 - 0.02   # leave room for the sell fees
        qty = min(risk_usd / per_share_risk, eq * inv.get("max_position_pct", 20.0) / 100 / est, cash / est)
        qty = _qty(qty, frac)
        if qty <= 0 or qty * est < inv.get("min_order_usd", 1.0):
            continue
        acc.s["orders"].append({"symbol": s, "side": "buy", "qty": qty, "stop_dist": dist, "day": str(day),
                                "reason": f"{p['name']} signal (score {score:.3f})"})
        cash -= qty * est
        room -= 1
        held.add(s)


def load_bars(symbols: list, period: str = "5y") -> dict:
    from . import data as md
    from zoneinfo import ZoneInfo
    raw = md.download(symbols, ZoneInfo("America/New_York"), period=period, interval="1d")
    return {s: indicators(df) for s, df in raw.items() if len(df) > 30}


def eligible(root: Path) -> list:
    w = json.loads((root / "strategy" / "watchlist.json").read_text())
    return [c["symbol"] for c in w["companies"] if c.get("active", True)]


def simulate(cfg: dict, bars: dict, params: dict, days: list, symbols: list, fx: float = 10.0) -> Account:
    c = dict(cfg)
    c["invest"] = {**cfg["invest"], "_eligible": set(symbols)}
    costs = CostModel({"costs": {**cfg["costs"], **cfg["invest"].get("costs", {})}})
    acc = Account.new(cfg["invest"]["initial_sek"], fx, cfg["capital"]["fx_conversion_fee_pct"], params, str(days[0]))
    rows = by_day(bars)
    for d in days:
        step(acc, d, rows.get(d, {}), costs, c)
        acc.s["last_day"] = str(d)
    return acc


def stats(acc: Account) -> dict:
    eq = pd.Series([e["equity"] for e in acc.s["equity"]])
    if eq.empty:
        return {"days": 0}
    start = acc.s["initial_usd"]
    dd = float(((eq - eq.cummax()) / eq.cummax()).min() * 100)
    t = acc.s["trades"]
    wins = [x for x in t if x["net"] > 0]
    gains, losses = sum(x["net"] for x in wins), -sum(x["net"] for x in t if x["net"] <= 0)
    return {"days": len(eq), "return_pct": round(100 * (eq.iloc[-1] / start - 1), 2), "max_drawdown_pct": round(dd, 2),
            "trades": len(t), "win_pct": round(100 * len(wins) / len(t), 1) if t else None,
            "profit_factor": round(gains / losses, 2) if losses > 0 else None,
            "avg_days_held": round(float(np.mean([x["days"] for x in t])), 1) if t else None,
            "fees_usd": round(sum(x["fees"] for x in t), 3), "open_positions": len(acc.s["positions"])}


def grid() -> list:
    out = []
    for dip in (0.08, 0.15):
        for rsi in (35, 45):
            for tp in (None, 0.25):
                out.append({**DEFAULT_PARAMS, "dip_pct": dip, "rsi_max": rsi, "take_profit": tp})
    for sa in (2.5, 4.0):
        out.append({"name": "trend_breakout", "stop_atr": sa, "trail_atr": sa + 1, "take_profit": None,
                    "max_hold_days": 120, "trend_exit": True})
    return out


def backtest(cfg: dict, root: Path, bars: dict | None = None) -> dict:
    syms = eligible(root)
    bench = json.loads((root / "strategy" / "watchlist.json").read_text()).get("benchmark", "QQQ")
    bars = bars or load_bars(sorted(set(syms) | {bench}))
    all_days = sorted({d.date() for f in bars.values() for d in f.index})
    rows = by_day(bars)
    days = [d for d in all_days if sum(1 for r in rows[d].values() if not pd.isna(r["sma200"])) >= 3]
    n_oos = max(1, len(days) // 3)
    ins, oos = days[:-n_oos], days[-n_oos:]
    rows = []
    for prm in grid():
        a_in, a_out = simulate(cfg, bars, prm, ins, syms), simulate(cfg, bars, prm, oos, syms)
        rows.append({"params": prm, "in_sample": stats(a_in), "out_of_sample": stats(a_out)})
    bench_rows = {}
    for label, ss in ((f"buy and hold {bench}", [bench]), ("buy and hold the whole watchlist (equal parts)", syms)):
        prm = {"name": "buy_hold", "stop_atr": 0, "trail_atr": None, "take_profit": None, "max_hold_days": None, "trend_exit": False}
        c2 = {**cfg, "invest": {**cfg["invest"], "max_risk_per_position_pct": 100, "max_position_pct": 100 / len(ss),
                                 "max_positions": len(ss), "daily_loss_limit_pct": 100}}
        bench_rows[label] = {"in_sample": stats(simulate(c2, bars, prm, ins, ss)), "out_of_sample": stats(simulate(c2, bars, prm, oos, ss))}
    eligible_rows = [r for r in rows if (r["in_sample"].get("trades") or 0) >= 10]
    best = max(eligible_rows or rows, key=lambda r: r["in_sample"].get("return_pct") or -1e9)
    res = {"date": datetime.now().date().isoformat(), "first_day": str(days[0]), "split_day": str(oos[0]), "last_day": str(days[-1]),
           "symbols": syms, "rows": rows, "benchmarks": bench_rows, "selected": best["params"]}
    _write_backtest(root, res)
    (root / "strategy" / "invest_selected.json").write_text(json.dumps(
        {"selected_at": res["date"], "rule": "Highest older-period return among variants with at least 10 older-period trades; "
         "the recent period is only reported.", "params": best["params"]}, indent=2) + "\n")
    return res


def _fmt(st: dict) -> str:
    if not st.get("days"):
        return "- | - | - | -"
    pf = st.get("profit_factor")
    return f"{st['return_pct']:+.1f}% | {st['max_drawdown_pct']:.1f}% | {st['trades']} | {pf if pf is not None else '-'}"


def _write_backtest(root: Path, res: dict) -> None:
    L = ["# Long-term investing: backtest (research only)", "",
         f"Real daily prices {res['first_day']} .. {res['last_day']}. Older period (rules chosen here) until {res['split_day']}, "
         "recent period after it (only reported). Each run starts from 500 SEK.", "",
         "**Important:** the watchlist was picked today, knowing which companies did well (for example NVIDIA). That makes "
         "every test on this list look better than reality. Compare with simply buying and holding, which has the same bias.", "",
         "| Strategy | Settings | Older: return | Older: worst drop | Older: trades | Older: profit factor | Recent: return | Recent: worst drop | Recent: trades | Recent: profit factor |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for name, b in res["benchmarks"].items():
        L.append(f"| **{name}** | (benchmark) | {_fmt(b['in_sample'])} | {_fmt(b['out_of_sample'])} |")
    for r in sorted(res["rows"], key=lambda r: r["in_sample"].get("return_pct") or -1e9, reverse=True):
        prm = {k: v for k, v in r["params"].items() if k != "name"}
        mark = " (selected)" if r["params"] == res["selected"] else ""
        L.append(f"| {r['params']['name']}{mark} | `{json.dumps(prm)}` | {_fmt(r['in_sample'])} | {_fmt(r['out_of_sample'])} |")
    L += ["", "_Return = change of the whole 500 SEK account in USD. Worst drop = largest fall from a high. Past results do not guarantee future results._", ""]
    (root / "reports" / "invest_backtest.md").write_text("\n".join(L))


# ---------------------------------------------------------------- live paper account

def state_path(root: Path) -> Path:
    return root / "ledger" / "invest.json"


def run_live(cfg: dict, root: Path, now: datetime | None = None, bars: dict | None = None, fx: float | None = None) -> str:
    from . import data as md
    from .market_calendar import MarketCalendar
    if not cfg.get("invest", {}).get("enabled"):
        return "Investing account is switched off in config.toml."
    cal = MarketCalendar(cfg)
    now = now or datetime.now(cal.tz)
    syms = eligible(root)
    held_or_ordered = set()
    p = state_path(root)
    acc = Account(json.loads(p.read_text())) if p.exists() else None
    if acc:
        held_or_ordered = set(acc.s["positions"]) | {o["symbol"] for o in acc.s["orders"]}
    all_syms = sorted(set(syms) | held_or_ordered)
    bars = bars or load_bars(all_syms, period="2y")
    # A day counts only once its close is final (16:15 New York or later).
    last_complete = now.date() if now.time() >= datetime.strptime("16:15", "%H:%M").time() else None
    days = sorted({d.date() for f in bars.values() for d in f.index})
    days = [d for d in days if cal.is_trading_day(d) and (d < now.date() or d == last_complete)]
    if not days:
        return "No finished trading day yet."
    if acc is None:
        fx = fx or md.usdsek(cfg["universe"]["fx_symbol"])
        sel = root / "strategy" / "invest_selected.json"
        params = json.loads(sel.read_text())["params"] if sel.exists() else DEFAULT_PARAMS
        acc = Account.new(cfg["invest"]["initial_sek"], fx, cfg["capital"]["fx_conversion_fee_pct"], params, str(days[-1]))
        acc.log(days[-1], f"Investing paper account opened with {cfg['invest']['initial_sek']:.0f} SEK; rules {json.dumps(params)}")
        todo = [days[-1]]
    else:
        last = pd.Timestamp(acc.s["last_day"]).date() if acc.s["last_day"] else None
        todo = [d for d in days if last is None or d > last]
    c = {**cfg, "invest": {**cfg["invest"], "_eligible": set(syms)}}
    costs = CostModel({"costs": {**cfg["costs"], **cfg["invest"].get("costs", {})}})
    rows = by_day(bars)
    for d in todo:
        step(acc, d, rows.get(d, {}), costs, c)
        acc.s["last_day"] = str(d)
    acc.s["fx_last"] = fx or acc.s.get("fx_last") or acc.s["fx_initial"]
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(acc.s, indent=1, default=str))
    write_report(root, acc)
    return f"Investing account updated through {acc.s['last_day']} ({len(todo)} day(s) processed)."


def write_report(root: Path, acc: Account) -> None:
    s = acc.s
    fx = s.get("fx_last") or s["fx_initial"]
    eq = s["equity"][-1]["equity"] if s["equity"] else s["initial_usd"]
    try:
        names = {c["symbol"]: c for c in json.loads((root / "strategy" / "watchlist.json").read_text())["companies"]}
    except Exception:
        names = {}
    L = ["# Long-term investing paper account", "",
         "_Simulated only. No real money, no brokerage connection._", "",
         f"* Started {s['start_day']} with {s['initial_sek']:.0f} SEK (= {s['initial_usd']:.2f} USD)",
         f"* Value now: {eq:.2f} USD = {eq * fx:.2f} SEK ({100 * (eq / s['initial_usd'] - 1):+.2f}% in USD)",
         f"* Cash: {s['cash']:.2f} USD; last processed day: {s['last_day']}",
         f"* Rules: `{json.dumps(s['params'])}`", "", "## Holdings", "",
         "| Company | Theme | Shares | Bought | Price paid | Last close | Stop | Result |", "|---|---|---|---|---|---|---|---|"]
    for sym, p in s["positions"].items():
        n = names.get(sym, {})
        L.append(f"| {n.get('name', sym)} ({sym}) | {n.get('theme', '')} | {p['qty']:g} | {p['entry_day']} | {p['entry']:.2f} | "
                 f"{p['last']:.2f} | {p['stop']:.2f} | {100 * (p['last'] / p['entry'] - 1):+.1f}% |")
    if not s["positions"]:
        L.append("| (none) | | | | | | | |")
    if s["orders"]:
        L += ["", "Orders for the next open: " + ", ".join(f"{o['side']} {o['symbol']}" for o in s["orders"])]
    L += ["", "## Closed positions", "", "| Company | Bought | Sold | Days | Why sold | Result USD |", "|---|---|---|---|---|---|"]
    for t in s["trades"][-30:]:
        L.append(f"| {t['symbol']} | {t['entry_day']} | {t['exit_day']} | {t['days']} | {t['exit_kind']} | {t['net']:+.3f} |")
    L += ["", "## Recent events", "", "```"] + s["events"][-25:] + ["```", ""]
    (root / "reports").mkdir(exist_ok=True)
    (root / "reports" / "invest.md").write_text("\n".join(L))
