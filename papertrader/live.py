"""Live paper-trading session runner (started by the GitHub Actions schedule).

One run = at most one session. The run decides what to do from the exchange calendar,
the control switch and the ledger, so starting it extra times is harmless:
  * not a trading day / nothing enabled / session already done -> exits immediately
  * too early -> exits (a later scheduled run takes over)
  * otherwise waits for 09:30 New York, checks the exchange really opened and the data is
    current (or skips the session safely), trades until 11:30, closes everything and reports.
"""
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable

import pandas as pd

from . import data as md
from . import report
from .control import read_local
from .costs import CostModel
from .engine import SessionEngine
from .features import compute_features
from .ledger import Ledger
from .market_calendar import MarketCalendar
from .risk import RiskManager
from .safety import assert_paper_only
from .strategies import build

FINAL = ("completed", "skipped", "stopped")


class YahooFeed:
    def __init__(self, cfg, tz):
        self.cfg, self.tz = cfg, tz

    def intraday(self, symbols, now):
        return md.intraday_today(symbols, self.tz, now)

    def bars_for_day(self, symbols, day):
        start = datetime.combine(day, datetime.min.time())
        data = md.download(symbols, self.tz, start=start.strftime("%Y-%m-%d"),
                           end=(start + timedelta(days=1)).strftime("%Y-%m-%d"), interval="1m")
        return {k: v[v.index.date == day] for k, v in data.items()}

    def daily(self, symbols):
        return md.daily(symbols, self.tz)

    def usdsek(self):
        return md.usdsek(self.cfg["universe"]["fx_symbol"])


@dataclass
class Runtime:
    root: Path
    cfg: dict
    feed: object
    now: Callable[[], datetime]
    sleep: Callable[[float], None] = time.sleep
    control: Callable[[], dict] | None = None
    persist: Callable[[str], None] = lambda msg: None
    notes: list = field(default_factory=list)


def ledger_path(root: Path, kind: str) -> Path:
    return root / "ledger" / f"{kind}.sqlite"


def selected_strategy(root: Path) -> dict:
    p = root / "strategy" / "selected.json"
    if not p.exists():
        return {"name": "no_trade", "params": {}}
    return json.loads(p.read_text())["strategy"]


def recover_open_positions(rt: Runtime, led: Ledger, cal: MarketCalendar, now: datetime) -> None:
    """Close positions left by an interrupted run whose trading window already ended, using
    the historical bar at/after that day's 11:30 (the documented execution model)."""
    costs, risk = CostModel(rt.cfg), RiskManager(rt.cfg, CostModel(rt.cfg))
    for day in sorted({p["day"] for p in led.positions()}):
        w = cal.window(datetime.fromisoformat(day).date())
        if w is None or now < w.end + timedelta(minutes=2):
            continue
        syms = [p["symbol"] for p in led.positions() if p["day"] == day]
        led.log(day, "WARN", f"Recovering positions left open by an interrupted run: {syms}")
        try:
            bars = rt.feed.bars_for_day(syms, w.day)
        except Exception as e:
            led.log(day, "ERROR", f"Could not fetch bars for recovery: {e}")
            bars = {}
        s = led.session(day)
        eng = SessionEngine(led, w, build(led.strategy_spec() or {"name": "no_trade"}), costs, risk, s["kind"] if s else "evaluation",
                            entries_allowed_from=pd.Timestamp(w.end), fx_usdsek=s["fx_usdsek"] if s else None)
        frames = {k: compute_features(v, w.open) for k, v in bars.items() if len(v)}
        eng.process(frames, data_fresh=False)
        if not eng.flat():
            eng.finalize_without_bars(pd.Timestamp(w.end))
        if s and s["status"] not in FINAL:
            led.mark_session(day, s["kind"], "completed", "resumed after an interruption; positions closed by recovery",
                             end_equity_usd=led.cash())
        rt.persist(f"recovered open positions for {day}")


def data_is_current(rt: Runtime, cal_tz, window, now: datetime) -> tuple[bool, str]:
    bench = rt.cfg["universe"]["benchmark"]
    try:
        bars = rt.feed.intraday([bench], now).get(bench)
    except Exception as e:
        return False, f"data error: {e}"
    if bars is None or bars.empty:
        return False, "no bars yet for the benchmark"
    last = bars.index[-1]
    if last < pd.Timestamp(window.open):
        return False, "no bar from today's regular session yet (exchange may not have opened)"
    lag = (pd.Timestamp(now) - (last + pd.Timedelta(minutes=1))).total_seconds()
    if lag > rt.cfg["risk"]["max_data_lag_seconds"]:
        return False, f"data is {lag:.0f} s old"
    return True, f"latest {bench} bar {last:%H:%M} New York, lag {max(lag, 0):.0f} s"


def run_once(rt: Runtime) -> str:
    cfg, root = rt.cfg, rt.root
    assert_paper_only(cfg)
    cal = MarketCalendar(cfg)
    now = rt.now()
    ctrl = (rt.control or (lambda: read_local(root)))()
    n_eval = cfg["schedule"]["evaluation_sessions"]

    # 1) Always first: never leave positions from an earlier day open.
    for kind in ("evaluation", "rehearsal"):
        if ledger_path(root, kind).exists():
            led = Ledger(ledger_path(root, kind))
            recover_open_positions(rt, led, cal, now)
            led.close()

    today = now.astimezone(cal.tz).date()
    w = cal.window(today)
    if w is None:
        return f"{today} is not a trading day on {cfg['schedule']['exchange']}; nothing to do."

    eval_led = Ledger(ledger_path(root, "evaluation"))
    eval_done = eval_led.completed_sessions("evaluation") >= n_eval
    eval_led.close()
    if ctrl.get("stop_requested"):
        return "Stop is switched on; not trading."
    if ctrl.get("evaluation_enabled") and not eval_done:
        kind = "evaluation"
    elif ctrl.get("rehearsal_date") == today.isoformat():
        kind = "rehearsal"
    elif eval_done:
        return "Evaluation finished; automatic trading is off."
    else:
        return "Evaluation not started (press Start in the Control workflow)."

    led = Ledger(ledger_path(root, kind))
    try:
        return _run_session(rt, cal, w, kind, led, n_eval)
    finally:
        led.close()


def _run_session(rt: Runtime, cal: MarketCalendar, w, kind: str, led: Ledger, n_eval: int) -> str:
    cfg, root = rt.cfg, rt.root
    day = w.day.isoformat()
    s = led.session(day)
    if s and s["status"] in FINAL:
        return f"{kind} session {day} already {s['status']}."
    now = rt.now()
    if now >= w.end:
        return f"Trading window for {day} has ended; nothing to do."
    wait = (w.start - now).total_seconds()
    if wait > cfg["schedule"]["max_wait_before_open_minutes"] * 60:
        return f"Too early ({wait / 60:.0f} min before the window); a later scheduled run will start the session."
    led.log(day, "INFO", f"{kind} run started; window {w.display(cal.display_tz)} "
                         f"({w.start:%H:%M}-{w.end:%H:%M} New York){' EARLY CLOSE DAY' if w.early_close else ''}")
    if wait > -60:
        rt.sleep(max(0.0, wait) + 65)  # first 1-minute bar completes at 09:31

    # 2) Exchange open + fresh data check, or skip safely.
    resuming = s is not None
    deadline = w.start + timedelta(minutes=cfg["schedule"]["data_check_deadline_minutes"])
    while True:
        now = rt.now()
        ok, msg = data_is_current(rt, cal.tz, w, now)
        if ok:
            led.log(day, "INFO", f"Data check passed: {msg}")
            break
        if now >= deadline and not resuming:
            led.mark_session(day, kind, "skipped", f"data check failed: {msg}")
            led.log(day, "ERROR", f"Session skipped safely: {msg}")
            rt.persist(f"{kind} {day}: skipped")
            write_reports(rt, cal, led, day, w, kind, n_eval)
            raise SessionSkipped(msg)
        if now >= w.end:
            break
        led.log(day, "INFO", f"Waiting for data: {msg}")
        rt.sleep(30)

    # 3) Account, strategy and universe.
    fx = rt.feed.usdsek()
    if led.account() is None:
        led.open_account(cfg["capital"]["initial_sek"], fx, cfg["capital"]["fx_conversion_fee_pct"], selected_strategy(root))
    strategy = build(led.strategy_spec())
    costs = CostModel(cfg)
    risk = RiskManager(cfg, costs)
    if not resuming:
        eq0 = led.cash() + sum(p["qty"] * p["avg_price"] for p in led.positions())
        liq = md.liquidity_table(rt.feed.daily(cfg["universe"]["symbols"]), pd.Timestamp(w.open))
        universe = md.select_universe(liq, cfg, eq0, costs) if not liq.empty else []
        led.start_session(day, kind, eq0, fx, universe)
        led.log(day, "INFO", f"Strategy {strategy.describe()}; start equity {eq0:.2f} USD ({eq0 * fx:.2f} SEK); "
                             f"{len(universe)} stocks fit the limits: {', '.join(universe) or 'none'}")
        entries_from = pd.Timestamp(w.start)
    else:
        universe = json.loads(led.session(day)["universe_json"] or "[]")
        entries_from = pd.Timestamp(rt.now()) - pd.Timedelta(minutes=2)
        led.log(day, "WARN", "Resuming an interrupted session; no new entries on bars from before this restart")
    rt.persist(f"{kind} {day}: session started")

    eng = SessionEngine(led, w, strategy, costs, risk, kind, entries_allowed_from=entries_from, fx_usdsek=fx)
    last_persist = time.monotonic()
    status = "completed"
    while True:
        now = rt.now()
        ctrl = (rt.control or (lambda: read_local(root)))()
        if ctrl.get("stop_requested") and not eng.stop_requested:
            eng.stop_requested = True
            led.log(day, "WARN", "STOP pressed: no new trades, closing all positions at the next bar")
        syms = sorted(set(universe) | {p["symbol"] for p in led.positions()})
        try:
            bars = rt.feed.intraday(syms, now) if syms else {}
            fresh = True
            newest = max((df.index[-1] for df in bars.values() if len(df)), default=None)
            if newest is None or (pd.Timestamp(now) - newest).total_seconds() > 60 + cfg["risk"]["max_data_lag_seconds"]:
                fresh = False
                led.log(day, "WARN", "Market data is stale; no new entries until it is current")
            frames = {k: compute_features(v, w.open) for k, v in bars.items() if len(v)}
            eng.process(frames, data_fresh=fresh)
        except Exception as e:  # keep running; exits are retried on the next poll
            led.log(day, "ERROR", f"Data/processing error, retrying: {e}")
        if eng.changed or time.monotonic() - last_persist > 600:
            rt.persist(f"{kind} {day}: update")
            eng.changed, last_persist = False, time.monotonic()
        if eng.stop_requested and eng.flat():
            status = "stopped"
            break
        if eng.halted and eng.flat():
            break
        if now >= w.end and eng.flat():
            break
        if now >= w.end + timedelta(minutes=15):
            eng.finalize_without_bars(pd.Timestamp(w.end))
            break
        rt.sleep(cfg["schedule"]["poll_seconds"])

    eq = led.cash()
    led.snapshot(day, eq, fx)
    led.mark_session(day, kind, status, "stopped by user" if status == "stopped" else "", end_equity_usd=eq)
    led.log(day, "INFO", f"Session {status}. End equity {eq:.2f} USD ({eq * fx:.2f} SEK); "
                         f"{len(led.trades(day))} round trips; no positions left open")
    write_reports(rt, cal, led, day, w, kind, n_eval)
    rt.persist(f"{kind} {day}: session {status}")
    return f"{kind} session {day} {status}"


class SessionSkipped(RuntimeError):
    pass


def write_reports(rt: Runtime, cal, led: Ledger, day: str, w, kind: str, n_eval: int) -> None:
    out = rt.root / "reports" / kind
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{day}.md").write_text(report.session_report(led, day, rt.cfg, w))
    if kind == "evaluation" and led.completed_sessions("evaluation") >= n_eval:
        if not (rt.root / "reports" / "evaluation_final.md").exists():
            sel_p = rt.root / "strategy" / "selected.json"
            sel = json.loads(sel_p.read_text()) if sel_p.exists() else None
            (rt.root / "reports" / "evaluation_final.md").write_text(report.final_report(led, rt.cfg, sel))
            led.log(day, "INFO", f"Evaluation complete ({n_eval} sessions). Automatic trading stops; final report written.")
    write_status(rt, cal)


def write_status(rt: Runtime, cal: MarketCalendar, note: str = "") -> None:
    p = ledger_path(rt.root, "evaluation")
    led = Ledger(p) if p.exists() else None
    ctrl = (rt.control or (lambda: read_local(rt.root)))()
    nxt = cal.next_window(rt.now())
    (rt.root / "STATUS.md").write_text(report.status_page(rt.root, rt.cfg, ctrl, led, nxt, note))
    if led:
        led.close()
