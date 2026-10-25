"""Research only: would a later daily deadline (up to the 16:00 close) have done better than 11:30?

The normal exits stay exactly the same (stop, target, trailing stop). Only the deadline moves:
whatever is still open at the deadline is sold. Two studies:
1. Real trades that were sold at 11:30 because of the deadline: what if they had been kept,
   with their stop and target still active, until the close?
2. Backtest on Yahoo's last ~30 days of real 1-minute bars: the same strategies with deadlines
   11:30, 13:00, 14:30 and 15:55, plus a version that may also buy later in the day.
Nothing here changes the live schedule or the strategy in use.
"""
import copy
import json
import sqlite3
from dataclasses import replace
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

from . import data as md
from .backtest import evaluate, load_history
from .costs import CostModel
from .strategies import build

DEADLINES = ["11:30", "13:00", "14:30", "15:55"]


def _with_deadline(hist: dict, hhmm: str, tz) -> dict:
    t = time.fromisoformat(hhmm)
    prep = {}
    for d, (w, frames, liq, market) in hist["prepared"].items():
        if w is not None:
            w = replace(w, end=min(w.close, datetime.combine(d, t, tz)))
        prep[d] = (w, frames, liq, market)
    return {**hist, "prepared": prep}


def _held_to_close(root: Path, cfg: dict) -> list:
    """Replays each real deadline exit past 11:30 with the same stop/target (and trailing stop)."""
    con = sqlite3.connect(root / "ledger" / "evaluation.sqlite")
    con.row_factory = sqlite3.Row
    trades = [dict(r) for r in con.execute("SELECT * FROM trades WHERE exit_kind LIKE 'window_end%' ORDER BY entry_time")]
    orders = {(o["day"], o["symbol"]): dict(o) for o in con.execute("SELECT * FROM orders WHERE side='buy'")}
    con.close()
    if not trades:
        return []
    tz = ZoneInfo("America/New_York")
    days = sorted({t["day"] for t in trades})
    start = datetime.fromisoformat(days[0]).replace(tzinfo=tz)
    end = datetime.fromisoformat(days[-1]).replace(tzinfo=tz) + pd.Timedelta(days=1)
    bars = md.intraday_range(sorted({t["symbol"] for t in trades}), tz, start, end)
    costs = CostModel(cfg)
    out = []
    for t in trades:
        o = orders.get((t["day"], t["symbol"]), {})
        df = bars.get(t["symbol"])
        row = {"day": t["day"], "symbol": t["symbol"], "qty": t["qty"], "entry": t["entry_price"],
               "sold_1130": t["exit_price"], "net_1130": t["net_pnl"]}
        if df is None or df.empty:
            out.append({**row, "note": "no Yahoo data for this day any more"})
            continue
        day = df[df.index.date == pd.Timestamp(t["day"]).date()]
        after = day[day.index >= pd.Timestamp(t["exit_time"])]
        after = after[after.index < pd.Timestamp(f"{t['day']} 16:00").tz_localize(tz)]
        stop, target, trail = o.get("stop"), o.get("target"), o.get("trail")
        hi = float(day[day.index < pd.Timestamp(t["exit_time"])]["High"].max()) if len(day) else None
        exit_px, kind, when = None, "close", None
        for ts, b in after.iterrows():
            if trail and hi is not None:
                hi = max(hi, float(b.High))
                stop = max(stop or 0, hi - trail)
            if stop and float(b.Low) <= stop:
                exit_px, kind, when = costs.stop_fill(stop, float(b.Open)), "stop", ts
                break
            if target and float(b.High) >= target:
                exit_px, kind, when = costs.sell_price(target), "target", ts
                break
        if exit_px is None:
            last = after.iloc[-1] if len(after) else day.iloc[-1]
            exit_px, when = costs.sell_price(float(last.Close)), after.index[-1] if len(after) else day.index[-1]
        gross = (exit_px - t["entry_price"]) * t["qty"]
        fees = costs.sell_fees(t["qty"], exit_px)
        net = gross - fees
        out.append({**row, "held_exit": round(float(exit_px), 4), "held_kind": kind,
                    "held_time": pd.Timestamp(when).tz_convert(tz).strftime("%H:%M"),
                    "net_held": round(float(net), 4), "high_after": round(float(after["High"].max()), 4) if len(after) else None,
                    "low_after": round(float(after["Low"].min()), 4) if len(after) else None})
    return out


def study(cfg: dict, root: Path) -> dict:
    tz = ZoneInfo("America/New_York")
    real = _held_to_close(root, cfg)
    late = copy.deepcopy(cfg)
    late["schedule"]["session_end"] = "15:55"
    hist = load_history(late, None)   # Yahoo only: the archive keeps bars only until ~11:40
    current = json.loads((root / "strategy" / "selected.json").read_text())["strategy"]
    try:
        con = sqlite3.connect(root / "ledger" / "evaluation.sqlite")
        current = json.loads(con.execute("SELECT strategy_json FROM account").fetchone()[0]) or current
        con.close()
    except Exception:
        pass
    specs = [current,
             {"name": "orb", "params": {"or_minutes": 5, "rvol_min": 2.0, "target_r": 2.5, "stop_atr": 2.0, "last_entry_minute": 90}},
             {"name": "momentum_leaders", "params": {"min_gain": 0.03, "rvol_min": 1.5, "trail_atr": 4.0, "take_profit": 0.03,
                                                     "first_minute": 15, "last_entry_minute": 75}}]
    seen, uniq = set(), []
    for s in specs:
        k = json.dumps(s, sort_keys=True)
        if k not in seen:
            seen.add(k)
            uniq.append(s)
    rows = []
    for spec in uniq:
        variants = [("buys in first ~1.5 h", spec)]
        allday = copy.deepcopy(spec)
        allday["params"]["last_entry_minute"] = 330   # may also buy until 15:00
        variants.append(("may also buy until 15:00", allday))
        for label, sp in variants:
            for dl in DEADLINES:
                if label.startswith("may") and dl == "11:30":
                    continue
                h = _with_deadline(hist, dl, tz)
                r, ins, oos, start_usd = evaluate(late, h, [build(sp)], oos_fraction=1 / 3)
                r = r[0]
                i, o = r["in_sample"], r["out_of_sample"]
                rows.append({"strategy": spec["name"], "entries": label, "deadline": dl,
                             "trades": (i.get("trades") or 0) + (o.get("trades") or 0),
                             "net_usd": round((i.get("net_pnl_usd") or 0) + (o.get("net_pnl_usd") or 0), 3),
                             "older_net": i.get("net_pnl_usd"), "recent_net": o.get("net_pnl_usd"),
                             "before_costs": round((i.get("gross_before_costs_usd") or 0) + (o.get("gross_before_costs_usd") or 0), 3),
                             "costs": round((i.get("modeled_costs_usd") or 0) + (o.get("modeled_costs_usd") or 0), 3),
                             "worst_dd_pct": min(i.get("max_drawdown_pct") or 0, o.get("max_drawdown_pct") or 0)})
    res = {"days": [d.isoformat() for d in hist["days"]], "real_trades": real, "backtest": rows}
    _write(root, res)
    return res


def _write(root: Path, res: dict) -> None:
    out = root / "reports"
    (out / "fullday_study.json").write_text(json.dumps(res, indent=2, default=str))
    L = ["# Study: later daily deadline (research only, live schedule unchanged)", "",
         f"History: {len(res['days'])} trading days of real Yahoo 1-minute bars ({res['days'][0]}..{res['days'][-1]})."
         if res["days"] else "No history.", "",
         "## 1. Real trades sold at the 11:30 deadline, replayed as if kept (same stop/target) until 16:00", "",
         "| Day | Stock | Shares | Entry | Sold at 11:30 | Net then | If kept: exit | How | Time NY | Net if kept |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for t in res["real_trades"]:
        if "note" in t:
            L.append(f"| {t['day']} | {t['symbol']} | {t['qty']} | {t['entry']:.4f} | {t['sold_1130']:.4f} | {t['net_1130']:+.4f} | {t['note']} | | | |")
        else:
            L.append(f"| {t['day']} | {t['symbol']} | {t['qty']} | {t['entry']:.4f} | {t['sold_1130']:.4f} | {t['net_1130']:+.4f} | "
                     f"{t['held_exit']:.4f} | {t['held_kind']} | {t['held_time']} | {t['net_held']:+.4f} |")
    L += ["", "## 2. Backtest: same rules, different deadline", "",
          "| Strategy | Buys allowed | Deadline (NY) | Trades | Net USD after costs | Older days | Recent days | Move before costs | Costs | Worst drawdown % |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in res["backtest"]:
        L.append(f"| {r['strategy']} | {r['entries']} | {r['deadline']} | {r['trades']} | {r['net_usd']:+.3f} | {r['older_net']} | {r['recent_net']} | "
                 f"{r['before_costs']:+.3f} | {r['costs']:.3f} | {r['worst_dd_pct']} |")
    L += ["", "_Each run starts from 500 SEK. Past results do not guarantee future results._", ""]
    (out / "fullday_study.md").write_text("\n".join(L))
