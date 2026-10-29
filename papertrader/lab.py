"""Strategy lab: extra simulated accounts that each try a different strategy, side by side.

Every lab account starts with its own 500 SEK of play money and trades the same live session
as the main account, with exactly the same costs, risk limits and 11:30 deadline. The lab
never touches the main account, its strategy or its readiness record; it only collects real,
forward-tested results for new ideas. Lab strategies are parameter sets in strategy/lab.json
(see RuleStrategy in strategies.py), so new ideas need no new code.

lab.json:
  {"accounts": [{"id": "spy_up_momentum", "spec": {...}, "added": "2026-10-29",
                 "why": "...", "active": true}]}
"""
import json
import re
from pathlib import Path

import pandas as pd

from .costs import CostModel
from .engine import SessionEngine
from .ledger import Ledger
from .risk import RiskManager
from .strategies import build


# Fixed retirement rules, decided in advance (a strategy is never judged on a few days):
RETIRE_MIN_SESSIONS = 20      # judged only after at least 20 sessions...
RETIRE_MIN_TRADES = 15        # ...and at least 15 trades
RETIRE_MAX_PROFIT_FACTOR = 0.8
RETIRE_HARD_SESSIONS = 40     # after 40 sessions, any account still losing money is retired
MAX_ACTIVE = 8                # at most 8 lab accounts trade at the same time


def retire_reason(r: dict) -> str | None:
    if r["sessions"] < RETIRE_MIN_SESSIONS or r["trades"] < RETIRE_MIN_TRADES or r["net_usd"] >= 0:
        return None
    if r.get("profit_factor") is not None and r["profit_factor"] < RETIRE_MAX_PROFIT_FACTOR:
        return (f"retired after {r['sessions']} sessions: lost {r['net_usd']:+.2f} USD over {r['trades']} trades, "
                f"profit factor {r['profit_factor']:.2f} (< {RETIRE_MAX_PROFIT_FACTOR})")
    if r["sessions"] >= RETIRE_HARD_SESSIONS:
        return f"retired after {r['sessions']} sessions: still losing ({r['net_usd']:+.2f} USD over {r['trades']} trades)"
    return None


def apply_retirements(root: Path, fx: float | None = None) -> list:
    """Stops lab accounts that have clearly failed. Their record is kept for the lessons."""
    p = lab_file(root)
    if not p.exists():
        return []
    doc = json.loads(p.read_text())
    done = []
    for a in doc.get("accounts", []):
        if not a.get("active", True):
            continue
        why = retire_reason(account_summary(root, a, fx))
        if why:
            a["active"], a["retired"] = False, why
            done.append((a["id"], why))
    if done:
        p.write_text(json.dumps(doc, indent=2) + "\n")
    return done


def lab_file(root: Path) -> Path:
    return root / "strategy" / "lab.json"


def entries(root: Path) -> list:
    p = lab_file(root)
    if not p.exists():
        return []
    out = []
    for a in json.loads(p.read_text()).get("accounts", []):
        if re.fullmatch(r"[a-z0-9_]{1,40}", a.get("id", "")):
            out.append(a)
    return out


def ledger_file(root: Path, acc_id: str) -> Path:
    return root / "ledger" / "lab" / f"{acc_id}.sqlite"


class Lab:
    """Runs all active lab accounts inside one live session. Errors here never stop the main account."""

    def __init__(self, root: Path, cfg: dict, w, fx: float, liq: pd.DataFrame | None, entries_from, log):
        self.accounts = []
        self.log = log
        self.day = w.day.isoformat()
        costs = CostModel(cfg)
        for a in [x for x in entries(root) if x.get("active", True)][:MAX_ACTIVE]:
            try:
                p = ledger_file(root, a["id"])
                p.parent.mkdir(parents=True, exist_ok=True)
                led = Ledger(p)
                if led.account() is None:
                    led.open_account(cfg["capital"]["initial_sek"], fx, cfg["capital"]["fx_conversion_fee_pct"], a["spec"])
                s = led.session(self.day)
                if s and s["status"] in ("completed", "stopped", "skipped"):
                    led.close()
                    continue
                if s is None:
                    from . import data as md
                    eq0 = led.cash()
                    universe = md.select_universe(liq, cfg, eq0, costs) if liq is not None and not liq.empty else []
                    led.start_session(self.day, "lab", eq0, fx, universe)
                    start = pd.Timestamp(w.start)
                else:
                    universe = json.loads(s["universe_json"] or "[]")
                    start = entries_from
                eng = SessionEngine(led, w, build(led.strategy_spec()), costs, RiskManager(cfg, costs), "lab",
                                    entries_allowed_from=start, fx_usdsek=fx)
                self.accounts.append({"id": a["id"], "led": led, "eng": eng, "universe": universe})
            except Exception as e:
                log(f"lab account {a.get('id')} not started: {e}")

    def symbols(self) -> set:
        out = set()
        for a in self.accounts:
            out |= set(a["universe"]) | {p["symbol"] for p in a["led"].positions()}
        return out

    def process(self, frames: dict, fresh: bool, market, stop: bool) -> bool:
        changed = False
        for a in self.accounts:
            try:
                eng = a["eng"]
                if stop:
                    eng.stop_requested = True
                mine = set(a["universe"]) | {p["symbol"] for p in a["led"].positions()}
                eng.process({k: v for k, v in frames.items() if k in mine}, data_fresh=fresh, market=market)
                changed |= eng.changed
                eng.changed = False
            except Exception as e:
                self.log(f"lab account {a['id']} error, retrying: {e}")
        return changed

    def flat(self) -> bool:
        return all(a["eng"].flat() for a in self.accounts)

    def finalize(self, end) -> None:
        for a in self.accounts:
            try:
                if not a["eng"].flat():
                    a["eng"].finalize_without_bars(end)
            except Exception as e:
                self.log(f"lab account {a['id']} finalize error: {e}")

    def finish(self, root: Path, fx: float, status: str) -> None:
        for a in self.accounts:
            led = a["led"]
            try:
                eq = led.cash()
                led.snapshot(self.day, eq, fx)
                led.mark_session(self.day, "lab", status, end_equity_usd=eq)
            finally:
                led.close()
        for acc_id, why in apply_retirements(root, fx):
            self.log(f"lab account {acc_id} {why}")
        write_leaderboard(root, fx)


def account_summary(root: Path, a: dict, fx: float | None = None) -> dict:
    p = ledger_file(root, a["id"])
    row = {"id": a["id"], "active": a.get("active", True), "why": a.get("why", ""), "added": a.get("added", ""),
           "spec": a["spec"], "sessions": 0, "trades": 0, "wins": 0, "net_usd": 0.0, "equity_sek": None, "start_sek": None}
    if not p.exists():
        return row
    led = Ledger(p)
    try:
        acc = led.account()
        if acc is None:
            return row
        trades = [dict(t) for t in led.trades()]
        sessions = [s for s in led.sessions("lab") if s["status"] == "completed"]
        fx = fx or acc["fx_usdsek_initial"]
        row.update(sessions=len(sessions), trades=len(trades), wins=sum(t["net_pnl"] > 0 for t in trades),
                   net_usd=round(sum(t["net_pnl"] for t in trades), 4), equity_sek=round(led.cash() * fx, 2),
                   start_sek=acc["initial_sek"], costs_usd=round(sum(t["costs"] or 0 for t in trades), 4))
        gains = sum(t["net_pnl"] for t in trades if t["net_pnl"] > 0)
        losses = -sum(t["net_pnl"] for t in trades if t["net_pnl"] <= 0)
        row["profit_factor"] = round(gains / losses, 3) if losses > 0 else None
        return row
    finally:
        led.close()


def write_leaderboard(root: Path, fx: float | None = None, main_row: dict | None = None) -> Path:
    rows = [account_summary(root, a, fx) for a in entries(root)]
    rows.sort(key=lambda r: r["net_usd"], reverse=True)
    L = ["# Strategy lab", "",
         "Extra simulated accounts, each with its own 500 SEK of play money, trading the same sessions as the "
         "main account with the same costs, limits and 11:30 deadline. They never affect the main account. "
         "A lab strategy is only worth promoting after many sessions; a few good days are often luck.", "",
         f"Retirement rule (fixed): judged only after {RETIRE_MIN_SESSIONS} sessions and {RETIRE_MIN_TRADES} trades; retired if losing "
         f"with profit factor below {RETIRE_MAX_PROFIT_FACTOR}, or still losing after {RETIRE_HARD_SESSIONS} sessions. Winners keep going. "
         "A retired account stops trading but its record is kept, so the lessons are not lost.", "",
         "| Rank | Lab account | Sessions | Trades | Winners | Net after costs USD | Account SEK | Active | Idea |",
         "|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        win = f"{100 * r['wins'] / r['trades']:.0f}%" if r["trades"] else "-"
        eq = f"{r['equity_sek']:.2f}" if r["equity_sek"] is not None else "-"
        L.append(f"| {i} | {r['id']} | {r['sessions']} | {r['trades']} | {win} | {r['net_usd']:+.3f} | {eq} | "
                 f"{'yes' if r['active'] else 'retired'} | {r['why']} |")
    gone = [a for a in entries(root) if a.get("retired")]
    if gone:
        L += ["", "## Retired", ""] + [f"* **{a['id']}**: {a['retired']}" for a in gone]
    L += ["", "## Rules each account uses", ""]
    for r in rows:
        L.append(f"* **{r['id']}** (added {r['added']}): `{json.dumps(r['spec'])}`")
    L.append("")
    p = root / "reports" / "lab.md"
    p.parent.mkdir(exist_ok=True)
    p.write_text("\n".join(L))
    return p
