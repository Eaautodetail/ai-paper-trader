"""The agent's self-assessment: is the paper-trading record strong enough to ask Albin to
consider real money? The criteria are fixed here in code (not in config) and decided in
advance, so they cannot be loosened to make the agent look ready. Meeting them only
produces a notification; real-money trading stays impossible in this program.
"""
from datetime import datetime

import numpy as np

from .ledger import Ledger

MIN_SESSIONS = 60            # about three months of trading days
MIN_TRADES = 100
RECENT_SESSIONS = 40
MIN_PROFIT_FACTOR = 1.3
MAX_DRAWDOWN_PCT = 10.0
STABLE_SESSIONS = 40         # sessions since the last strategy change
BLOCK = 20                   # blocks of 20 sessions; at least 2 of the last 3 must be positive


def _bootstrap_lower(x: np.ndarray, n: int = 5000, q: float = 0.05) -> float:
    rng = np.random.default_rng(12345)
    means = rng.choice(x, size=(n, len(x)), replace=True).mean(axis=1)
    return float(np.quantile(means, q))


def assess(led: Ledger) -> dict:
    sessions = [s for s in led.sessions() if s["kind"] in ("evaluation", "training") and s["status"] == "completed"]
    trades = [t for t in led.trades()]
    a = led.account()
    crit = []

    def add(name, ok, value, need):
        crit.append({"name": name, "ok": bool(ok), "value": value, "need": need})

    add("Paper-trading sessions", len(sessions) >= MIN_SESSIONS, len(sessions), f">= {MIN_SESSIONS}")
    add("Completed trades", len(trades) >= MIN_TRADES, len(trades), f">= {MIN_TRADES}")
    recent = sessions[-RECENT_SESSIONS:]
    recent_pnl = sum((s["end_equity_usd"] or 0) - (s["start_equity_usd"] or 0) for s in recent)
    add(f"Profit after all costs, last {RECENT_SESSIONS} sessions", len(recent) >= RECENT_SESSIONS and recent_pnl > 0,
        f"{recent_pnl:+.2f} USD", "> 0 over a full 40 sessions")
    last = np.array([t["net_pnl"] for t in trades[-MIN_TRADES:]])
    lower = _bootstrap_lower(last) if len(last) >= 20 else None
    add("Average trade is profitable with 95% confidence (last 100 trades)", lower is not None and lower > 0 and len(last) >= MIN_TRADES,
        "-" if lower is None else f"lower bound {lower:+.4f} USD per trade", "lower bound > 0")
    wins, losses = last[last > 0].sum() if len(last) else 0, -last[last <= 0].sum() if len(last) else 0
    pf = wins / losses if losses > 0 else (float("inf") if wins > 0 else 0.0)
    add("Profit factor (gains / losses, last 100 trades)", pf >= MIN_PROFIT_FACTOR and len(last) >= MIN_TRADES,
        f"{pf:.2f}" if np.isfinite(pf) else "no losses yet", f">= {MIN_PROFIT_FACTOR}")
    eq = [a["initial_usd"]] + [s["end_equity_usd"] for s in sessions if s["end_equity_usd"] is not None] if a else []
    dd = 0.0
    if len(eq) > 1:
        e = np.array(eq)
        dd = float(((np.maximum.accumulate(e) - e) / np.maximum.accumulate(e)).max() * 100)
    add("Largest drop from a high (drawdown)", dd <= MAX_DRAWDOWN_PCT and len(sessions) >= MIN_SESSIONS, f"{dd:.1f}%", f"<= {MAX_DRAWDOWN_PCT:.0f}%")
    blocks = [sessions[i:i + BLOCK] for i in range(max(0, len(sessions) - 3 * BLOCK), len(sessions), BLOCK)]
    blocks = [b for b in blocks if len(b) == BLOCK]
    pos = sum(1 for b in blocks if sum((s["end_equity_usd"] or 0) - (s["start_equity_usd"] or 0) for s in b) > 0)
    add("Consistency: positive 20-session blocks (of the last 3)", len(blocks) == 3 and pos >= 2, f"{pos} of {len(blocks)}", "at least 2 of 3")
    changes = [e["ts"] for e in led.events(None, limit=1000) if e["message"].startswith("Strategy changed")]
    last_change = max(changes) if changes else ""
    stable = sum(1 for s in sessions if (s["started_at"] or "") > last_change)
    add("Same strategy for the whole recent record", stable >= STABLE_SESSIONS, f"{stable} sessions", f">= {STABLE_SESSIONS}")
    ready = all(c["ok"] for c in crit)
    return {"ready": ready, "met": sum(c["ok"] for c in crit), "total": len(crit), "criteria": crit,
            "checked_at": datetime.now().isoformat(timespec="minutes")}


def markdown(res: dict) -> str:
    lines = ["# Readiness self-assessment", "",
             "The agent checks itself after every session against fixed rules decided in advance. "
             "Real-money trading is never switched on by this program; \"ready\" only means: worth your review.", "",
             f"**Verdict: {'READY FOR YOUR REVIEW' if res['ready'] else 'NOT READY - still training'} "
             f"({res['met']} of {res['total']} criteria met)**", "",
             "| Criterion | Now | Needed | Met |", "|---|---|---|---|"]
    for c in res["criteria"]:
        lines.append(f"| {c['name']} | {c['value']} | {c['need']} | {'yes' if c['ok'] else 'no'} |")
    lines += ["", "Why so strict: a few good days happen by luck. These rules require months of results, "
              "enough trades to measure, profit after every cost, and the same strategy throughout.", ""]
    return "\n".join(lines)
