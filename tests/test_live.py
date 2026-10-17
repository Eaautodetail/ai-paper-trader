"""End-to-end runs of the scheduled job with a fake clock and fake (synthetic) data feed."""
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

from papertrader import control
from papertrader.ledger import Ledger
from papertrader.live import Runtime, SessionSkipped, ledger_path, run_once, write_status

from conftest import FakeClock, FakeFeed, breakout_path, flat_path, make_day, small_universe_cfg

NY = ZoneInfo("America/New_York")


def strat_file(root, spec):
    (root / "strategy" / "selected.json").write_text(json.dumps({"strategy": spec}))


def days_feed(days, path=breakout_path):
    out = {}
    for d in days:
        a = make_day(d, 4.0, path)
        a.loc[a.index[16:22], "Volume"] = 300_000
        out[d] = {"AAA": a, "BBB": make_day(d, 5.0, flat_path), "SPY": make_day(d, 500.0, flat_path)}
    return FakeFeed(out)


def rt_for(root, cfg, feed, t):
    clock = FakeClock(t)
    return Runtime(root, cfg, feed, now=clock.now, sleep=clock.sleep), clock


def test_not_started_does_nothing(cfg, tmp_root):
    c = small_universe_cfg(cfg)
    rt, _ = rt_for(tmp_root, c, days_feed(["2026-10-15"]), datetime(2026, 10, 15, 9, 0, tzinfo=NY))
    assert "not started" in run_once(rt).lower()


def test_holiday_does_nothing(cfg, tmp_root):
    c = small_universe_cfg(cfg)
    control.write(tmp_root, evaluation_enabled=True)
    rt, _ = rt_for(tmp_root, c, days_feed([]), datetime(2026, 11, 26, 9, 0, tzinfo=NY))
    assert "not a trading day" in run_once(rt)


def test_too_early_exits(cfg, tmp_root):
    c = small_universe_cfg(cfg)
    control.write(tmp_root, evaluation_enabled=True)
    rt, _ = rt_for(tmp_root, c, days_feed(["2026-10-15"]), datetime(2026, 10, 15, 7, 0, tzinfo=NY))
    assert "too early" in run_once(rt).lower()


def test_full_evaluation_three_sessions_then_stops(cfg, tmp_root):
    c = small_universe_cfg(cfg)
    c["training"]["enabled"] = False
    control.write(tmp_root, evaluation_enabled=True)
    strat_file(tmp_root, {"name": "orb", "params": {"or_minutes": 15, "rvol_min": 1.2, "target_r": 2.5}})
    c["risk"]["min_reward_to_cost"] = 0.5  # synthetic moves are small; let the mechanics run
    days = ["2026-10-15", "2026-10-16", "2026-10-19", "2026-10-20"]
    feed = days_feed(days)
    for d in days[:3]:
        y, m, dd = map(int, d.split("-"))
        rt, clock = rt_for(tmp_root, c, feed, datetime(y, m, dd, 8, 50, tzinfo=NY))
        msg = run_once(rt)
        assert "completed" in msg, msg
        assert clock.now() >= datetime(y, m, dd, 11, 30, tzinfo=NY)
        assert (tmp_root / "reports" / "evaluation" / f"{d}.md").exists()
    led = Ledger(ledger_path(tmp_root, "evaluation"))
    assert led.completed_sessions("evaluation") == 3
    assert not led.positions()
    assert led.account()["initial_sek"] == 500
    eq = led.cash()
    assert all(pd.Timestamp(t["exit_time"]) <= pd.Timestamp(t["day"] + " 11:30").tz_localize(NY) for t in led.trades())
    led.close()
    assert (tmp_root / "reports" / "evaluation_final.md").exists()
    # fourth trading day: nothing happens any more
    rt, _ = rt_for(tmp_root, c, feed, datetime(2026, 10, 20, 9, 0, tzinfo=NY))
    assert "finished" in run_once(rt).lower()
    led = Ledger(ledger_path(tmp_root, "evaluation"))
    assert led.cash() == eq and led.session("2026-10-20") is None
    write_status(rt, __import__("papertrader.market_calendar", fromlist=["x"]).MarketCalendar(c))
    assert "EVALUATION FINISHED" in (tmp_root / "STATUS.md").read_text()


def test_second_run_same_day_is_harmless(cfg, tmp_root):
    c = small_universe_cfg(cfg)
    control.write(tmp_root, evaluation_enabled=True)
    strat_file(tmp_root, {"name": "orb", "params": {}})
    feed = days_feed(["2026-10-15"])
    rt, _ = rt_for(tmp_root, c, feed, datetime(2026, 10, 15, 9, 0, tzinfo=NY))
    run_once(rt)
    led = Ledger(ledger_path(tmp_root, "evaluation"))
    n = len(led.orders())
    led.close()
    rt, _ = rt_for(tmp_root, c, feed, datetime(2026, 10, 15, 9, 40, tzinfo=NY))
    assert "already completed" in run_once(rt)
    led = Ledger(ledger_path(tmp_root, "evaluation"))
    assert len(led.orders()) == n


def test_stale_data_skips_session_safely(cfg, tmp_root):
    c = small_universe_cfg(cfg)
    control.write(tmp_root, evaluation_enabled=True)
    feed = days_feed(["2026-10-15"])
    feed.fail = True
    rt, _ = rt_for(tmp_root, c, feed, datetime(2026, 10, 15, 9, 0, tzinfo=NY))
    try:
        run_once(rt)
        assert False, "expected skip"
    except SessionSkipped:
        pass
    led = Ledger(ledger_path(tmp_root, "evaluation"))
    assert led.session("2026-10-15")["status"] == "skipped"
    assert led.completed_sessions("evaluation") == 0 and not led.orders()


def test_stop_button_closes_positions(cfg, tmp_root):
    c = small_universe_cfg(cfg)
    c["risk"]["min_reward_to_cost"] = 0.5
    control.write(tmp_root, evaluation_enabled=True)
    strat_file(tmp_root, {"name": "orb", "params": {"or_minutes": 15, "rvol_min": 1.2, "target_r": 5}})
    feed = days_feed(["2026-10-15"])
    clock = FakeClock(datetime(2026, 10, 15, 9, 0, tzinfo=NY))

    def ctrl():
        stop = clock.now() >= datetime(2026, 10, 15, 9, 55, tzinfo=NY)
        return {"evaluation_enabled": True, "stop_requested": stop, "rehearsal_date": None}

    from papertrader.live import Runtime
    rt = Runtime(tmp_root, c, feed, now=clock.now, sleep=clock.sleep, control=ctrl)
    msg = run_once(rt)
    assert "stopped" in msg
    led = Ledger(ledger_path(tmp_root, "evaluation"))
    assert not led.positions()
    assert led.completed_sessions("evaluation") == 0
    assert clock.now() < datetime(2026, 10, 15, 10, 5, tzinfo=NY)


def test_recovery_closes_leftover_positions_next_day(cfg, tmp_root):
    c = small_universe_cfg(cfg)
    control.write(tmp_root, evaluation_enabled=True)
    strat_file(tmp_root, {"name": "orb", "params": {}})
    feed = days_feed(["2026-10-15", "2026-10-16"])
    led = Ledger(ledger_path(tmp_root, "evaluation"))
    led.open_account(500, 10.0, 0.25, {"name": "orb", "params": {}})
    led.start_session("2026-10-15", "evaluation", led.cash(), 10.0, ["AAA"])
    oid = led.add_order("x", "2026-10-15", "AAA", "buy", 1, "2026-10-15T09:45:00-04:00", "orb", "t", 3.0, 9.0)
    led.record_buy(oid, "AAA", 1, 4.0, "2026-10-15T09:45:00-04:00", 0, 0.0, 3.0, 9.0, "2026-10-15", "orb")
    led.close()  # the run "crashed" with an open position
    rt, _ = rt_for(tmp_root, c, feed, datetime(2026, 10, 16, 8, 50, tzinfo=NY))
    run_once(rt)
    led = Ledger(ledger_path(tmp_root, "evaluation"))
    t = [t for t in led.trades() if t["day"] == "2026-10-15"][0]
    assert t["exit_kind"] == "window_end"
    assert pd.Timestamp(t["exit_time"]) == pd.Timestamp("2026-10-15 11:30", tz=NY)
    assert led.session("2026-10-15")["status"] == "completed"


def test_rehearsal_uses_separate_ledger(cfg, tmp_root):
    c = small_universe_cfg(cfg)
    control.write(tmp_root, rehearsal_date="2026-10-15")
    strat_file(tmp_root, {"name": "orb", "params": {}})
    rt, _ = rt_for(tmp_root, c, days_feed(["2026-10-15"]), datetime(2026, 10, 15, 9, 0, tzinfo=NY))
    assert "rehearsal session 2026-10-15 completed" in run_once(rt)
    assert ledger_path(tmp_root, "rehearsal").exists()
    led = Ledger(ledger_path(tmp_root, "evaluation"))
    assert led.account() is None


def test_training_continues_after_evaluation_in_same_account(cfg, tmp_root):
    c = small_universe_cfg(cfg)
    c["risk"]["min_reward_to_cost"] = 0.5
    c["training"]["weekdays"] = [1]  # Tuesdays
    control.write(tmp_root, evaluation_enabled=True)
    strat_file(tmp_root, {"name": "orb", "params": {"or_minutes": 15, "rvol_min": 1.2, "target_r": 2.5}})
    days = ["2026-10-15", "2026-10-16", "2026-10-19", "2026-10-20", "2026-10-21"]
    feed = days_feed(days)
    for d in days[:3]:
        y, m, dd = map(int, d.split("-"))
        rt, _ = rt_for(tmp_root, c, feed, datetime(y, m, dd, 8, 50, tzinfo=NY))
        assert "evaluation session" in run_once(rt)
    led = Ledger(ledger_path(tmp_root, "evaluation"))
    cash_after_eval = led.cash()
    led.close()
    rt, _ = rt_for(tmp_root, c, feed, datetime(2026, 10, 20, 8, 50, tzinfo=NY))  # Tuesday
    assert "training session 2026-10-20 completed" in run_once(rt)
    rt, _ = rt_for(tmp_root, c, feed, datetime(2026, 10, 21, 8, 50, tzinfo=NY))  # Wednesday: not a training day
    assert "not today" in run_once(rt)
    led = Ledger(ledger_path(tmp_root, "evaluation"))
    assert led.session("2026-10-20")["kind"] == "training"
    assert led.session("2026-10-20")["start_equity_usd"] == cash_after_eval  # same account carries on
    assert led.account()["initial_sek"] == 500 and led.completed_sessions("evaluation") == 3
    assert (tmp_root / "reports" / "training" / "2026-10-20.md").exists()
    assert "NOT READY" in (tmp_root / "reports" / "readiness.md").read_text()
    assert not (tmp_root / "reports" / "READY_FOR_REVIEW.md").exists()
    assert (tmp_root / "data" / "bars" / "2026-10-20.csv.gz").exists()
    write_status(rt, __import__("papertrader.market_calendar", fromlist=["x"]).MarketCalendar(c))
    assert "TRAINING" in (tmp_root / "STATUS.md").read_text()


def test_public_repo_trains_every_weekday(cfg, monkeypatch):
    from datetime import date
    from papertrader.live import training_day
    wed = date(2026, 10, 21)
    monkeypatch.setenv("PAPERTRADER_REPO_PRIVATE", "true")
    assert not training_day(cfg, wed)
    monkeypatch.setenv("PAPERTRADER_REPO_PRIVATE", "false")
    assert training_day(cfg, wed)
    monkeypatch.delenv("PAPERTRADER_REPO_PRIVATE")
    assert not training_day(cfg, wed)  # unknown visibility: assume private
