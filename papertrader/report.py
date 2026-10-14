"""Markdown reports: per session, the status page, and the final evaluation report."""
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .ledger import Ledger

DISCLAIMER = ("Simulated paper trading only. No real money, no brokerage connection. "
              "Results from a few sessions are an operational test, not evidence of a profitable strategy.")


def _sek(usd: float | None, fx: float | None) -> str:
    if usd is None:
        return "-"
    return f"{usd:.2f} USD" + (f" ({usd * fx:.2f} SEK)" if fx else "")


def _local(ts: str | None, tz: str) -> str:
    if not ts:
        return "-"
    return datetime.fromisoformat(ts).astimezone(ZoneInfo(tz)).strftime("%H:%M")


def session_report(led: Ledger, day: str, cfg: dict, window=None) -> str:
    s = led.session(day)
    fx = s["fx_usdsek"] if s else None
    ny, st = cfg["schedule"]["exchange_timezone"], cfg["schedule"]["display_timezone"]
    trades = led.trades(day)
    orders = led.orders(day)
    events = list(reversed(led.events(day, limit=2000)))
    skips = Counter(e["message"].split("rejected: ")[-1] for e in events if e["level"] == "SKIP")
    warns = [e["message"] for e in events if e["level"] in ("WARN", "ERROR")]
    net = sum(t["net_pnl"] for t in trades)
    costs = sum(t["costs"] for t in trades)
    lines = [f"# {s['kind'].capitalize() if s else ''} session {day}", "", f"_{DISCLAIMER}_", ""]
    if window:
        lines.append(f"* Window: {window.start:%H:%M}-{window.end:%H:%M} New York = "
                     f"{window.start.astimezone(ZoneInfo(st)):%H:%M}-{window.end.astimezone(ZoneInfo(st)):%H:%M} Stockholm"
                     + (" (early close day)" if window.early_close else ""))
    if s:
        lines += [f"* Status: **{s['status']}**" + (" (daily loss limit hit)" if s["halted"] else "") + (f" - {s['note']}" if s["note"] else ""),
                  f"* Start equity: {_sek(s['start_equity_usd'], fx)}",
                  f"* End equity: {_sek(s['end_equity_usd'], fx)}",
                  f"* Session P&L after all costs: {_sek((s['end_equity_usd'] or 0) - (s['start_equity_usd'] or 0), fx) if s['end_equity_usd'] is not None else '-'}",
                  f"* USD/SEK used: {fx:.4f}" if fx else "* USD/SEK: -",
                  f"* Stocks watched ({len(json.loads(s['universe_json'] or '[]'))}): {', '.join(json.loads(s['universe_json'] or '[]')) or '-'}"]
    lines += [f"* Orders: {len(orders)}; completed round trips: {len(trades)}; net {net:.4f} USD; modeled costs {costs:.4f} USD", "",
              "## Trades", "", "| Stock | Shares | Entry (Stockholm) | Entry USD | Exit (Stockholm) | Exit USD | Exit reason | Net P&L USD | Costs USD |",
              "|---|---|---|---|---|---|---|---|---|"]
    for t in trades:
        lines.append(f"| {t['symbol']} | {t['qty']} | {_local(t['entry_time'], st)} | {t['entry_price']:.4f} | {_local(t['exit_time'], st)} | "
                     f"{t['exit_price']:.4f} | {t['exit_kind']} | {t['net_pnl']:.4f} | {t['costs']:.4f} |")
    if not trades:
        lines.append("| (no trades) | | | | | | | | |")
    lines += ["", "## Signals the risk manager rejected", ""]
    lines += [f"* {n} x {why}" for why, n in skips.most_common(10)] or ["* none"]
    lines += ["", "## Warnings", ""] + ([f"* {w}" for w in warns] or ["* none"])
    lines += ["", "## Full event log", "", "```"] + [f"{_local(e['ts'], st)} {e['level']:5} {e['message']}" for e in events] + ["```", ""]
    return "\n".join(lines)


def status_page(root: Path, cfg: dict, ctrl: dict, eval_led: Ledger | None, next_window, note: str = "") -> str:
    st = ZoneInfo(cfg["schedule"]["display_timezone"])
    n = cfg["schedule"]["evaluation_sessions"]
    lines = ["# Paper-trading status", "",
             "**Mode: PAPER TRADING (simulated). Real-money trading: DISABLED - there is no brokerage connection in this program.**", "",
             f"* Updated: {datetime.now(st):%Y-%m-%d %H:%M} Stockholm time"]
    done = eval_led.completed_sessions("evaluation") if eval_led else 0
    if ctrl.get("stop_requested"):
        state = "STOPPED (press Start in the Control workflow to resume)"
    elif done >= n:
        state = f"EVALUATION FINISHED ({done}/{n} sessions). Automatic trading is off. Read reports/evaluation_final.md"
    elif ctrl.get("evaluation_enabled"):
        state = f"RUNNING - {done}/{n} evaluation sessions completed"
    else:
        state = "NOT STARTED - press Start in the Control workflow"
    lines.append(f"* Evaluation: **{state}**")
    if next_window:
        lines.append(f"* Next trading window: {next_window.start.astimezone(st):%a %Y-%m-%d %H:%M}-{next_window.end.astimezone(st):%H:%M} Stockholm "
                     f"({next_window.start:%H:%M}-{next_window.end:%H:%M} New York)")
    if ctrl.get("rehearsal_date"):
        lines.append(f"* Rehearsal (test session, separate ledger) scheduled for: {ctrl['rehearsal_date']}")
    if eval_led and eval_led.account():
        a = eval_led.account()
        fx = a["fx_usdsek_initial"]
        last = eval_led.db.execute("SELECT * FROM equity ORDER BY ts DESC LIMIT 1").fetchone()
        eq = last["equity_usd"] if last else a["cash_usd"]
        fx_now = (last["fx_usdsek"] if last and last["fx_usdsek"] else fx)
        lines += [f"* Starting capital: {a['initial_sek']:.2f} SEK (= {a['initial_usd']:.2f} USD after a {a['fx_fee_sek']:.2f} SEK conversion fee)",
                  f"* Current equity: {eq:.2f} USD = {eq * fx_now:.2f} SEK at USD/SEK {fx_now:.4f}",
                  f"* Cash: {a['cash_usd']:.2f} USD",
                  f"* Strategy (frozen for the evaluation): `{a['strategy_json']}`"]
        pos = eval_led.positions()
        lines.append(f"* Open positions: {', '.join(f'{p['qty']} {p['symbol']}' for p in pos) if pos else 'none'}")
        lines += ["", "| Session | Kind | Status | Start equity USD | End equity USD | Trades |", "|---|---|---|---|---|---|"]
        for s in eval_led.sessions():
            lines.append(f"| [{s['day']}](reports/evaluation/{s['day']}.md) | {s['kind']} | {s['status']} | "
                         f"{(s['start_equity_usd'] or 0):.2f} | {(s['end_equity_usd'] or 0):.2f} | {len(eval_led.trades(s['day']))} |")
    if note:
        lines += ["", f"Last run: {note}"]
    lines += ["", f"_{DISCLAIMER}_", ""]
    return "\n".join(lines)


def final_report(led: Ledger, cfg: dict, backtest_sel: dict | None) -> str:
    a = led.account()
    sessions = [s for s in led.sessions("evaluation")]
    trades = led.trades()
    fx0 = a["fx_usdsek_initial"]
    last = led.db.execute("SELECT * FROM equity ORDER BY ts DESC LIMIT 1").fetchone()
    fx1 = last["fx_usdsek"] if last and last["fx_usdsek"] else fx0
    eq = led.cash()
    net = sum(t["net_pnl"] for t in trades)
    costs = sum(t["costs"] for t in trades)
    wins = [t for t in trades if t["net_pnl"] > 0]
    by_exit = Counter(t["exit_kind"] for t in trades)
    lines = ["# Evaluation report (3 paper-trading sessions)", "", f"_{DISCLAIMER}_", "",
             "Automatic trading has stopped. Live trading was never enabled and cannot be enabled by this program.", "",
             "## Money", "",
             f"* Starting capital: {a['initial_sek']:.2f} SEK -> {a['initial_usd']:.4f} USD (USD/SEK {fx0:.4f}, conversion fee {a['fx_fee_sek']:.2f} SEK)",
             f"* Final equity: {eq:.4f} USD = {eq * fx1:.2f} SEK at USD/SEK {fx1:.4f}",
             f"* Trading result: {eq - a['initial_usd']:+.4f} USD ({100 * (eq / a['initial_usd'] - 1):+.3f}%) after all modeled costs",
             f"* Result in SEK incl. the conversion fee and currency moves: {eq * fx1 - a['initial_sek']:+.2f} SEK",
             f"* Modeled transaction costs (spread, slippage, fees): {costs:.4f} USD", "",
             "## Activity", "",
             f"* Sessions: " + ", ".join(f"{s['day']} ({s['status']})" for s in sessions),
             f"* Round trips: {len(trades)}; winners {len(wins)}; losers {len(trades) - len(wins)}",
             f"* Exits: " + (", ".join(f"{k} {v}" for k, v in by_exit.items()) or "none"),
             f"* Net P&L from trades: {net:.4f} USD", "",
             "## Session results", "", "| Session | Status | Start USD | End USD | P&L USD | Trades |", "|---|---|---|---|---|---|"]
    for s in sessions:
        lines.append(f"| [{s['day']}](evaluation/{s['day']}.md) | {s['status']} | {(s['start_equity_usd'] or 0):.4f} | {(s['end_equity_usd'] or 0):.4f} | "
                     f"{((s['end_equity_usd'] or 0) - (s['start_equity_usd'] or 0)):+.4f} | {len(led.trades(s['day']))} |")
    lines += ["", "## Strategy", "", f"* Used: `{a['strategy_json']}`"]
    if backtest_sel and "data" in backtest_sel:
        lines += [f"* Chosen by backtest on {backtest_sel['data']['first_day']}..{backtest_sel['data']['last_day']}; "
                  f"passed out-of-sample check: {'yes' if backtest_sel.get('validated_out_of_sample') else 'no'} (see backtest.md)"]
    lines += ["", "## How to read this", "",
              "* Three sessions are far too few to judge profitability; the goal was to prove the system runs safely and records everything.",
              "* Check that every position was closed by 11:30 New York time (exit reason `window_end` or earlier) and that no limits were broken.",
              "* With 500 SEK, one position may be at most 20% (about 100 SEK), so only cheaper stocks fit and fixed fees weigh heavily.",
              "* Nothing switches to real money. Any next step is your decision.", ""]
    return "\n".join(lines)
