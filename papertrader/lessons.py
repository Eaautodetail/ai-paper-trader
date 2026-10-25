"""Trade lessons: what did winning and losing trades have in common at the moment of buying?

For every trade it looks up the 1-minute bar the buy decision was made on and records simple
traits (time of day, gain since the open, volume surge, distance above VWAP, volatility, how
the whole market (SPY) was doing, and how large the costs were compared with the trade).
Trades are then grouped by each trait to show where the money was made or lost.

Two samples:
* real paper trades (updated after every session, bars from data/bars/)
* the current strategy replayed over all stored history (updated by the weekly review)
Analysis only: nothing here changes a strategy or a limit by itself. A pattern only becomes a
rule after it has been added as a fixed strategy variant and passed the weekly walk-forward test.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .features import compute_features

MIN_GROUP = 5   # groups with fewer trades are shown but not called out as a pattern

TRAITS = [
    ("entry_minute", "Minutes after the open", [0, 15, 30, 45, 60, 90, 400]),
    ("gain_open_pct", "Stock's gain since the open, %", [-100, 0, 1, 2, 3, 5, 100]),
    ("rvol", "Volume vs normal (x)", [0, 1.5, 2, 3, 5, 1e9]),
    ("vwap_dist_atr", "Price above VWAP, in ATRs", [-100, 0, 1, 2, 3, 100]),
    ("atr_pct", "Volatility: 1-min ATR as % of price", [0, 0.1, 0.2, 0.3, 0.5, 100]),
    ("spy_gain_pct", "Market (SPY) since the open, %", [-100, -0.3, 0, 0.3, 100]),
    ("cost_pct", "Costs as % of the trade", [0, 0.3, 0.5, 0.75, 1, 100]),
    ("price", "Share price, USD", [0, 3, 5, 8, 12, 1e9]),
]


def _signal_row(frame: pd.DataFrame, entry_time) -> pd.Series | None:
    if frame is None or frame.empty:
        return None
    before = frame[frame.index < pd.Timestamp(entry_time)]
    return before.iloc[-1] if len(before) else None


def traits(trades: list, frames_by_day: dict, market_by_day: dict) -> pd.DataFrame:
    rows = []
    for t in trades:
        day = str(t["day"])[:10]
        f = frames_by_day.get(day, {}).get(t["symbol"])
        r = _signal_row(f, t["entry_time"])
        if r is None:
            continue
        m = _signal_row(market_by_day.get(day), t["entry_time"])
        size = float(t["entry_price"]) * float(t["qty"])
        net, cost = float(t["net_pnl"]), float(t["costs"] or 0)
        rows.append({
            "day": day, "symbol": t["symbol"], "exit_kind": t["exit_kind"],
            "entry_minute": int(r["minute"]) + 1,
            "gain_open_pct": 100 * float(r["ret_open"]),
            "rvol": float(r["rvol"]) if pd.notna(r["rvol"]) else np.nan,
            "vwap_dist_atr": (float(r["Close"]) - float(r["vwap"])) / float(r["atr"]) if r["atr"] else np.nan,
            "atr_pct": 100 * float(r["atr"]) / float(r["Close"]),
            "spy_gain_pct": 100 * float(m["ret_open"]) if m is not None else np.nan,
            "cost_pct": 100 * cost / size if size else np.nan,
            "price": float(t["entry_price"]),
            "net": net, "move_pct": 100 * (net + cost) / size if size else np.nan,
            "win": net > 0,
        })
    return pd.DataFrame(rows)


def group_table(df: pd.DataFrame, col: str, bins: list) -> pd.DataFrame:
    d = df.dropna(subset=[col])
    if d.empty:
        return pd.DataFrame()
    cats = pd.cut(d[col], bins=bins, right=False)
    g = d.groupby(cats, observed=True)
    return pd.DataFrame({"trades": g.size(), "win_pct": 100 * g["win"].mean(), "avg_net": g["net"].mean(),
                         "total_net": g["net"].sum(), "avg_move_pct": g["move_pct"].mean()})


def _label(iv) -> str:
    lo, hi = iv.left, iv.right
    if lo <= -100:
        return f"below {hi:g}"
    if hi >= 100:
        return f"{lo:g} or more"
    return f"{lo:g} to {hi:g}"


def summarize(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"trades": 0}
    out = {"trades": int(len(df)), "win_pct": round(100 * df["win"].mean(), 1),
           "net": round(float(df["net"].sum()), 4), "avg_move_pct": round(float(df["move_pct"].mean()), 3),
           "avg_cost_pct": round(float(df["cost_pct"].mean()), 3),
           "exits": df["exit_kind"].value_counts().to_dict(), "patterns": [], "tables": {}}
    for col, title, bins in TRAITS:
        tab = group_table(df, col, bins)
        if tab.empty:
            continue
        out["tables"][col] = [{"group": _label(iv), **{k: round(float(v), 4) for k, v in row.items()}}
                              for iv, row in tab.iterrows()]
        big = tab[tab["trades"] >= MIN_GROUP]
        if len(big) >= 2:
            best, worst = big["avg_net"].idxmax(), big["avg_net"].idxmin()
            if big.loc[best, "avg_net"] - big.loc[worst, "avg_net"] > 0:
                out["patterns"].append(
                    f"{title}: best when **{_label(best)}** ({int(big.loc[best, 'trades'])} trades, "
                    f"{big.loc[best, 'win_pct']:.0f}% winners, avg {big.loc[best, 'avg_net']:+.3f} USD), worst when "
                    f"**{_label(worst)}** ({int(big.loc[worst, 'trades'])} trades, {big.loc[worst, 'win_pct']:.0f}% winners, "
                    f"avg {big.loc[worst, 'avg_net']:+.3f} USD)")
    return out


def _section(title: str, s: dict, note: str) -> list:
    L = [f"## {title}", "", note, ""]
    if not s.get("trades"):
        return L + ["No trades with stored bars yet.", ""]
    L += [f"* Trades: {s['trades']}; winners: {s['win_pct']}%; total net after costs: {s['net']:+.3f} USD",
          f"* Average price move before costs: {s['avg_move_pct']:+.2f}% per trade; average costs: {s['avg_cost_pct']:.2f}% per trade",
          f"* How trades ended: " + ", ".join(f"{k} {v}" for k, v in s["exits"].items()), ""]
    if s["patterns"]:
        L += ["**What stands out** (groups of at least %d trades):" % MIN_GROUP, ""] + [f"* {p}" for p in s["patterns"]] + [""]
    else:
        L += [f"_Too few trades per group (needs {MIN_GROUP}) to call out patterns yet._", ""]
    names = {c: t for c, t, _ in TRAITS}
    for col, rows in s["tables"].items():
        L += [f"<details><summary>{names[col]}</summary>", "", "| Group | Trades | Winners % | Avg net USD | Total net USD | Avg move before costs % |",
              "|---|---|---|---|---|---|"]
        L += [f"| {r['group']} | {int(r['trades'])} | {r['win_pct']:.0f} | {r['avg_net']:+.4f} | {r['total_net']:+.4f} | {r['avg_move_pct']:+.2f} |"
              for r in rows]
        L += ["", "</details>", ""]
    return L


def real_trade_traits(root: Path, led, tz) -> pd.DataFrame:
    from . import archive
    bars = archive.load(root, tz)
    trades = [dict(t) for t in led.trades()]
    frames, market = {}, {}
    for day in sorted({t["day"] for t in trades}):
        d = pd.Timestamp(day).date()
        for s in {t["symbol"] for t in trades if t["day"] == day} | {"SPY"}:
            df = bars.get(s)
            if df is None:
                continue
            one = df[df.index.date == d]
            if len(one) < 5:
                continue
            f = compute_features(one, pd.Timestamp(f"{day} 09:30").tz_localize(tz))
            if s == "SPY":
                market[day] = f
            else:
                frames.setdefault(day, {})[s] = f
    return traits(trades, frames, market)


def history_trade_traits(trades: list, prepared: dict) -> pd.DataFrame:
    frames = {d.isoformat(): p[1] for d, p in prepared.items()}
    market = {d.isoformat(): p[3] for d, p in prepared.items() if p[3] is not None}
    return traits(trades, frames, market)


def write(root: Path, real: dict | None = None, history: dict | None = None) -> Path:
    out = root / "reports"
    out.mkdir(exist_ok=True)
    cache = out / "trade_lessons.json"
    saved = json.loads(cache.read_text()) if cache.exists() else {}
    if real is not None:
        saved["real"] = real
    if history is not None:
        saved["history"] = history
    cache.write_text(json.dumps(saved, indent=2, default=str))
    L = ["# Trade lessons", "",
         "What winning and losing trades had in common at the moment of buying. Analysis only: a pattern "
         "becomes a rule only after it is added as a fixed strategy variant and passes the weekly walk-forward test.", ""]
    L += _section("Real paper trades", saved.get("real", {}),
                  "All simulated trades so far, updated after every session.")
    h = saved.get("history", {})
    L += _section("Current strategy replayed on all stored history", h,
                  f"Strategy `{json.dumps(h.get('strategy'))}` over {h.get('days', 0)} trading days, updated by the weekly review. "
                  "Larger sample, so patterns here are more reliable than in the real trades.")
    p = out / "trade_lessons.md"
    p.write_text("\n".join(L))
    return p
