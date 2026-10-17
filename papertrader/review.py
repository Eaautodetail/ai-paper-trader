"""Weekly learning step (runs on Saturdays, never during a trading day).

1. Re-tests every candidate strategy on all real 1-minute history available: the growing
   archive in data/bars/ plus Yahoo's last ~30 days, with the same simulator and costs.
2. Ranks variants on the earlier days and checks them on the most recent third (out of sample).
3. Switches the paper-trading strategy only if a candidate clearly beats the current one on
   both parts of the history. Otherwise it keeps the current one.
The review can only choose among the fixed, tested strategies in strategies.py. It cannot edit
code, change risk limits or touch real money.
"""
import json
from datetime import datetime
from pathlib import Path

from .backtest import evaluate, load_history
from .ledger import Ledger
from .strategies import build, candidate_grid

MIN_IS_TRADES = 10
MIN_OOS_TRADES = 3
SWITCH_MARGIN_PCT = 0.5     # must beat the current strategy by at least 0.5% of starting equity


def _score(r):
    return (r["in_sample"].get("net_pnl_usd") or 0) + (r["out_of_sample"].get("net_pnl_usd") or 0)


def decide(rows: list, current: dict, start_usd: float, evaluation_done: bool) -> tuple[dict | None, str]:
    cur = next((r for r in rows if r["strategy"] == current), None)
    eligible = [r for r in rows if r["strategy"]["name"] != "no_trade"
                and (r["in_sample"].get("trades") or 0) >= MIN_IS_TRADES
                and (r["out_of_sample"].get("trades") or 0) >= MIN_OOS_TRADES]
    if not evaluation_done:
        return None, "The 3-session evaluation is still running; the strategy is not changed during it."
    if not eligible:
        return None, "No candidate traded often enough to judge; keeping the current strategy."
    best = max(eligible, key=_score)
    if cur is None:
        return best["strategy"], "Current strategy was not in the test set; switching to the best tested one."
    if best["strategy"] == current:
        return None, "The current strategy is still the best tested one; keeping it."
    margin = SWITCH_MARGIN_PCT / 100 * start_usd
    better_total = _score(best) - _score(cur) > margin
    better_recent = (best["out_of_sample"].get("net_pnl_usd") or 0) > (cur["out_of_sample"].get("net_pnl_usd") or 0)
    if better_total and better_recent:
        return best["strategy"], (f"Switching: {best['strategy']['name']} beat the current strategy by "
                                  f"{_score(best) - _score(cur):+.2f} USD over all tested days and also on the most recent days.")
    return None, "No candidate beat the current strategy clearly enough on both older and recent days; keeping it."


def weekly_review(cfg: dict, root: Path, hist: dict | None = None) -> dict:
    led = Ledger(root / "ledger" / "evaluation.sqlite")
    try:
        current = led.strategy_spec() or json.loads((root / "strategy" / "selected.json").read_text())["strategy"]
        cands = candidate_grid()
        if all(c.describe() != current for c in cands):
            cands.append(build(current))
        hist = hist or load_history(cfg, root)
        rows, ins, oos, start_usd = evaluate(cfg, hist, cands)
        done = led.completed_sessions("evaluation") >= cfg["schedule"]["evaluation_sessions"]
        new, why = decide(rows, current, start_usd, done)
        if new is not None and led.account() is not None:
            led.set_strategy(new, "weekly review: " + why)
        result = {"date": datetime.now().date().isoformat(), "days": len(hist["days"]),
                  "in_sample": len(ins), "out_of_sample": len(oos), "current": current,
                  "new": new, "why": why}
        _write(root, rows, result)
        return result
    finally:
        led.close()


def _write(root: Path, rows: list, res: dict) -> None:
    out = root / "reports"
    out.mkdir(exist_ok=True)
    top = sorted(rows, key=_score, reverse=True)[:12]
    lines = ["# Weekly strategy review", "",
             f"* Date: {res['date']}; history: {res['days']} trading days of real 1-minute data "
             f"({res['in_sample']} older days used for ranking, {res['out_of_sample']} recent days for checking)",
             f"* Strategy before the review: `{json.dumps(res['current'])}`",
             f"* Decision: **{res['why']}**",
             f"* Strategy from now on: `{json.dumps(res['new'] or res['current'])}`", "",
             "Top candidates (net USD after all costs, starting from 500 SEK each time):", "",
             "| Strategy | Params | Older days: trades / net | Recent days: trades / net | Move before costs | Costs |",
             "|---|---|---|---|---|---|"]
    for r in top:
        i, o = r["in_sample"], r["out_of_sample"]
        lines.append(f"| {r['strategy']['name']} | `{json.dumps(r['strategy']['params'])}` | {i.get('trades', 0)} / {i.get('net_pnl_usd', 0):+.2f} | "
                     f"{o.get('trades', 0)} / {o.get('net_pnl_usd', 0):+.2f} | "
                     f"{(i.get('gross_before_costs_usd') or 0) + (o.get('gross_before_costs_usd') or 0):+.2f} | "
                     f"{(i.get('modeled_costs_usd') or 0) + (o.get('modeled_costs_usd') or 0):.2f} |")
    lines += ["", "_Past results do not guarantee future results. The review can only pick among fixed, tested strategies._", ""]
    (out / "weekly_review.md").write_text("\n".join(lines))
    log = out / "learning_log.md"
    head = "# Learning log\n\n| Date | Days of history | Decision |\n|---|---|---|\n"
    text = log.read_text() if log.exists() else head
    log.write_text(text + f"| {res['date']} | {res['days']} | {res['why']} |\n")
