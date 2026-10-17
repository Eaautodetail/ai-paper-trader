import copy
import math
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from papertrader import safety
from papertrader.costs import CostModel
from papertrader.engine import SessionEngine
from papertrader.features import compute_features
from papertrader.ledger import Ledger
from papertrader.risk import RiskContext, RiskManager
from papertrader.strategies import OpeningRangeBreakout, Signal, Strategy, candidate_grid

from conftest import breakout_path, flat_path, make_day

NY = ZoneInfo("America/New_York")
STO = ZoneInfo("Europe/Stockholm")


# ---------------------------------------------------------------- safety
def test_refuses_non_paper_config(cfg):
    bad = copy.deepcopy(cfg)
    bad["mode"]["paper_trading"] = False
    with pytest.raises(safety.SafetyError):
        safety.assert_paper_only(bad)
    bad["mode"]["paper_trading"] = True
    bad["mode"]["live"] = True
    with pytest.raises(safety.SafetyError):
        safety.assert_paper_only(bad)


def test_live_flag_is_hard_false():
    assert safety.LIVE_TRADING_ENABLED is False


def test_no_brokerage_code_in_package():
    """The package must contain no brokerage SDKs or order endpoints."""
    banned = ["alpaca", "ib_insync", "ibapi", "tradier", "robin_stocks", "/v2/orders", "submit_order",
              "place_order", "ccxt", "oanda", "tastytrade", "schwab", "etrade", "webull", "nordnet", "avanza_api"]
    pkg = Path(__file__).resolve().parent.parent / "papertrader"
    for f in pkg.glob("*.py"):
        text = f.read_text().lower()
        for b in banned:
            assert b not in text, f"{b} found in {f.name}"


def test_risk_limits_cannot_be_loosened(cfg):
    loose = copy.deepcopy(cfg)
    loose["risk"]["max_position_pct_equity"] = 50
    with pytest.raises(AssertionError):
        RiskManager(loose, CostModel(loose))


# ---------------------------------------------------------------- calendar
def test_calendar_holidays_and_early_close(cal):
    assert not cal.is_trading_day(date(2026, 11, 26))  # Thanksgiving
    assert not cal.is_trading_day(date(2026, 12, 25))
    assert not cal.is_trading_day(date(2026, 10, 17))  # Saturday
    w = cal.window(date(2026, 11, 27))                 # day after Thanksgiving closes 13:00
    assert w.early_close and w.close.hour == 13 and w.end.strftime("%H:%M") == "11:30"


def test_window_times_and_daylight_saving(cal):
    w = cal.window(date(2026, 10, 15))
    assert (w.start.strftime("%H:%M"), w.end.strftime("%H:%M")) == ("09:30", "11:30")
    assert w.start.astimezone(STO).strftime("%H:%M") == "15:30"
    # Sweden leaves summer time on 25 Oct, the US on 1 Nov: one week with a 5-hour gap
    assert cal.window(date(2026, 10, 27)).start.astimezone(STO).strftime("%H:%M") == "14:30"
    assert cal.window(date(2026, 11, 2)).start.astimezone(STO).strftime("%H:%M") == "15:30"
    assert cal.window(date(2027, 3, 16)).start.astimezone(STO).strftime("%H:%M") == "14:30"  # US summer time first


# ---------------------------------------------------------------- costs
def test_costs(cfg):
    c = CostModel(cfg)
    assert c.buy_price(5.0) == pytest.approx(5.0 + 0.005 + 0.0025)
    assert c.sell_price(5.0) == pytest.approx(5.0 - 0.005 - 0.0025)
    assert c.sell_fees(1, 5.0) == pytest.approx(0.02)  # SEC and TAF each round up to a cent
    assert c.sell_fees(0, 5.0) == 0
    assert c.stop_fill(4.9, 4.8) == pytest.approx(c.sell_price(4.8))  # gap through the stop


# ---------------------------------------------------------------- risk manager
def ctx(**kw):
    base = dict(equity=50.0, cash=50.0, session_start_equity=50.0, session_pnl=0.0, open_symbols=set(),
                pending_symbols=set(), traded_symbols=set(), entries_today=0, in_window=True, data_fresh=True, halted=False)
    base.update(kw)
    return RiskContext(**base)


def sig(price=4.0, stop=3.95, target=4.5, sym="AAA"):
    return Signal(sym, pd.Timestamp("2026-10-15 09:45", tz=NY), price, stop, target, "test", "test")


def test_position_never_exceeds_20pct(cfg):
    rm = RiskManager(cfg, CostModel(cfg))
    d = rm.evaluate(sig(price=1.0 * 3, stop=2.99, target=3.5), ctx(equity=1000, cash=1000, session_start_equity=1000))
    assert d.approved
    assert d.qty * d.est_entry <= 0.20 * 1000 + 1e-9


def test_per_trade_loss_limit(cfg):
    rm = RiskManager(cfg, CostModel(cfg))
    d = rm.evaluate(sig(price=3.0, stop=2.5, target=4.5), ctx(equity=1000, cash=1000, session_start_equity=1000))
    assert d.approved and d.planned_loss <= 0.005 * 1000 + 1e-9


def test_rejects_when_one_share_too_expensive(cfg):
    rm = RiskManager(cfg, CostModel(cfg))
    d = rm.evaluate(sig(price=12.0, stop=11.9, target=13.0), ctx())
    assert not d.approved and "20% position limit" in d.reason


def test_rejects_outside_window_stale_data_halt_and_short(cfg):
    rm = RiskManager(cfg, CostModel(cfg))
    assert not rm.evaluate(sig(), ctx(in_window=False)).approved
    assert not rm.evaluate(sig(), ctx(data_fresh=False)).approved
    assert not rm.evaluate(sig(), ctx(session_pnl=-1.0)).approved  # -2% of 50 = -1.0
    assert not rm.evaluate(sig(price=4.0, stop=4.1, target=3.0), ctx()).approved  # short-style levels


def test_rejects_when_costs_eat_the_gain(cfg):
    rm = RiskManager(cfg, CostModel(cfg))
    d = rm.evaluate(sig(price=4.0, stop=3.95, target=4.02), ctx())
    assert not d.approved and "costs" in d.reason


# ---------------------------------------------------------------- ledger
def test_ledger_idempotency_and_no_reset(tmp_path):
    led = Ledger(tmp_path / "l.sqlite")
    led.open_account(500, 10.0, 0.25, {"name": "no_trade"})
    cash = led.cash()
    led.open_account(500, 9.0, 0.25, {"name": "orb"})  # must not reset
    assert led.cash() == cash and led.strategy_spec()["name"] == "no_trade"
    assert led.add_order("k1", "2026-10-15", "AAA", "buy", 1, "t", "s", "r", 1, 2) is not None
    assert led.add_order("k1", "2026-10-15", "AAA", "buy", 1, "t", "s", "r", 1, 2) is None
    led.close()
    led2 = Ledger(tmp_path / "l.sqlite")  # survives a restart
    assert led2.cash() == cash and len(led2.orders()) == 1


def test_ledger_blocks_short_sale(tmp_path):
    led = Ledger(tmp_path / "l.sqlite")
    led.open_account(500, 10.0, 0.25, {})
    oid = led.add_order("s", "d", "AAA", "sell", 1, "t")
    with pytest.raises(ValueError):
        led.record_sell(oid, "AAA", 1, 5.0, "t", 0, 0, 0, "x")


# ---------------------------------------------------------------- engine
class BuyAt(Strategy):
    """Test strategy: one signal at a given minute with fixed stop/target distances."""
    def __init__(self, minute=20, stop_pct=0.01, target_pct=0.04):
        super().__init__("buy_at", dict(minute=minute, stop_pct=stop_pct, target_pct=target_pct))

    def signal(self, symbol, f, i):
        r = f.iloc[i]
        if r.minute != self.params["minute"]:
            return None
        return Signal(symbol, f.index[i], float(r.Close), float(r.Close * (1 - self.params["stop_pct"])),
                      float(r.Close * (1 + self.params["target_pct"])), self.name, "test")


def setup_engine(cfg, cal, tmp_path, strategy, day="2026-10-15", start_eq_fx=10.0):
    led = Ledger(tmp_path / "e.sqlite")
    led.quiet = True
    led.open_account(500, start_eq_fx, 0.25, strategy.describe())
    w = cal.window(date.fromisoformat(day))
    led.start_session(day, "evaluation", led.cash(), start_eq_fx, ["AAA"])
    costs = CostModel(cfg)
    eng = SessionEngine(led, w, strategy, costs, RiskManager(cfg, costs), "evaluation", fx_usdsek=start_eq_fx)
    return led, eng, w


def feats(df, w):
    return {"AAA": compute_features(df, w.open)}


def test_entry_fills_at_next_bar_open_and_target_exit(cfg, cal, tmp_path):
    led, eng, w = setup_engine(cfg, cal, tmp_path, BuyAt(minute=20, stop_pct=0.01, target_pct=0.02))
    df = make_day("2026-10-15", 4.0, breakout_path)
    eng.process(feats(df, w))
    buy = [o for o in led.orders() if o["side"] == "buy"][0]
    t_fill = pd.Timestamp(buy["fill_time"])
    assert t_fill == df.index[21]  # signal on bar 20 -> fill at open of bar 21
    assert buy["fill_price"] == pytest.approx(CostModel(cfg).buy_price(df["Open"].iloc[21]))
    t = led.trades()[0]
    assert t["exit_kind"] == "target"
    assert eng.flat()


def test_stop_exit_and_loss_within_limit(cfg, cal, tmp_path):
    led, eng, w = setup_engine(cfg, cal, tmp_path, BuyAt(minute=20, stop_pct=0.01, target_pct=0.05))
    df = make_day("2026-10-15", 4.0, lambda i: 1.0 if i <= 22 else 0.97)
    eng.process(feats(df, w))
    t = led.trades()[0]
    assert t["exit_kind"] == "stop"
    eq0 = led.session("2026-10-15")["start_equity_usd"]
    assert -t["net_pnl"] <= 0.005 * eq0 + 0.03  # gap below the stop can add slippage beyond the plan


def test_everything_closed_at_1130_and_no_entries_after(cfg, cal, tmp_path):
    led, eng, w = setup_engine(cfg, cal, tmp_path, BuyAt(minute=100, stop_pct=0.02, target_pct=0.5))
    df = make_day("2026-10-15", 4.0, flat_path)
    eng.process(feats(df, w))
    t = led.trades()[0]
    assert t["exit_kind"] == "window_end"
    assert pd.Timestamp(t["exit_time"]) == pd.Timestamp("2026-10-15 11:30", tz=NY)
    assert eng.flat() and not led.positions()
    # a signal at 11:30 or later is never traded
    led2, eng2, w2 = setup_engine(cfg, cal, tmp_path / "b", BuyAt(minute=120))
    eng2.process(feats(df, w2))
    assert not led2.orders()


def test_restart_does_not_duplicate(cfg, cal, tmp_path):
    led, eng, w = setup_engine(cfg, cal, tmp_path, BuyAt(minute=20, stop_pct=0.01, target_pct=0.5))
    df = make_day("2026-10-15", 4.0, flat_path)
    eng.process(feats(df.iloc[:40], w))
    n_orders = len(led.orders())
    # simulate a crash and a new process continuing from the stored progress
    eng2 = SessionEngine(led, w, eng.strategy, eng.costs, eng.risk, "evaluation", fx_usdsek=10.0)
    eng2.process(feats(df.iloc[:40], w))
    assert len(led.orders()) == n_orders
    eng2.process(feats(df, w))
    assert len([o for o in led.orders() if o["side"] == "buy"]) == 1 and eng2.flat()


def test_daily_loss_limit_halts_and_flattens(cfg, cal, tmp_path):
    c = copy.deepcopy(cfg)
    c["risk"]["max_risk_per_trade_pct_equity"] = 0.5
    led, eng, w = setup_engine(c, cal, tmp_path, BuyAt(minute=20, stop_pct=0.30, target_pct=0.5))
    # wide stop is allowed only for a tiny size; force a big loss by crashing the price
    df = make_day("2026-10-15", 4.0, lambda i: 1.0 if i < 25 else 0.75)
    eng.process(feats(df, w))
    s = led.session("2026-10-15")
    assert not led.positions()
    if led.trades():  # a trade happened: verify halt or stop handled it and the loss cap held
        assert -sum(t["net_pnl"] for t in led.trades()) <= 0.02 * s["start_equity_usd"] + 0.6


def test_orb_signal_on_breakout():
    df = make_day("2026-10-15", 4.0, breakout_path, vol=50_000)
    df.loc[df.index[20:24], "Volume"] = 200_000
    f = compute_features(df, df.index[0])
    s = OpeningRangeBreakout(or_minutes=15, rvol_min=1.5)
    sigs = [s.signal("AAA", f, i) for i in range(len(f))]
    hits = [x for x in sigs if x]
    assert hits and hits[0].bar_time >= df.index[15]
    assert all(h.stop < h.ref_price < h.target for h in hits)


def test_features_are_causal():
    df = make_day("2026-10-15", 4.0, breakout_path)
    full = compute_features(df, df.index[0])
    part = compute_features(df.iloc[:50], df.index[0])
    cols = ["vwap", "ema9", "atr", "rsi", "or15_high"]
    pd.testing.assert_frame_equal(full[cols].iloc[:50], part[cols])


def test_candidate_grid_has_baseline():
    names = {s.name for s in candidate_grid()}
    assert {"no_trade", "orb", "vwap_trend", "vwap_reversion"} <= names


# ---------------------------------------------------------------- trailing stop / momentum
class BuyTrail(Strategy):
    def __init__(self, minute=20, trail_pct=0.01):
        super().__init__("buy_trail", dict(minute=minute, trail_pct=trail_pct))

    def signal(self, symbol, f, i):
        r = f.iloc[i]
        if r.minute != self.params["minute"]:
            return None
        trail = float(r.Close) * self.params["trail_pct"]
        return Signal(symbol, f.index[i], float(r.Close), float(r.Close) - trail, float(r.Close) * 2, self.name,
                      "test", trail=trail)


def test_trailing_stop_follows_price_up_and_exits_in_profit(cfg, cal, tmp_path):
    led, eng, w = setup_engine(cfg, cal, tmp_path, BuyTrail(minute=20, trail_pct=0.01))
    # rises 3% then falls back 5%
    df = make_day("2026-10-15", 4.0, lambda i: 1.0 if i <= 20 else (1 + 0.001 * (i - 20) if i <= 50 else 1.03 - 0.002 * (i - 50)))
    eng.process(feats(df, w))
    t = led.trades()[0]
    assert t["exit_kind"] == "stop"
    assert t["exit_price"] > t["entry_price"]  # the stop had moved above the entry
    assert pd.Timestamp(t["exit_time"]) > df.index[50]


def test_highest_score_signal_goes_first(cfg, cal, tmp_path):
    class Two(Strategy):
        def __init__(self):
            super().__init__("two", {})

        def signal(self, symbol, f, i):
            r = f.iloc[i]
            if r.minute != 20:
                return None
            return Signal(symbol, f.index[i], float(r.Close), float(r.Close) * 0.99, float(r.Close) * 1.05, "two", "t",
                          score={"AAA": 1.0, "BBB": 5.0}[symbol])
    c = copy.deepcopy(cfg)
    c["risk"]["max_open_positions"] = 1
    led, eng, w = setup_engine(c, cal, tmp_path, Two())
    df = make_day("2026-10-15", 4.0, flat_path)
    eng.process({"AAA": compute_features(df, w.open), "BBB": compute_features(df, w.open)})
    assert [o["symbol"] for o in led.orders() if o["side"] == "buy"] == ["BBB"]


def test_momentum_leaders_signal():
    from papertrader.strategies import MomentumLeaders
    df = make_day("2026-10-15", 4.0, lambda i: 1.0 + 0.001 * i + (0.002 * (i - 24) if i >= 25 else 0))
    df.loc[df.index[25:30], "Volume"] = 300_000
    f = compute_features(df, df.index[0])
    s = MomentumLeaders(min_gain=0.02, rvol_min=1.5)
    hits = [x for x in (s.signal("AAA", f, i) for i in range(len(f))) if x]
    assert hits and all(h.trail > 0 and h.stop < h.ref_price < h.target for h in hits)
    assert all(f.loc[h.bar_time, "ret_open"] >= 0.02 for h in hits)


def test_old_ledger_files_are_upgraded(tmp_path):
    import sqlite3
    from papertrader.ledger import SCHEMA
    p = tmp_path / "old.sqlite"
    db = sqlite3.connect(p)
    db.executescript(SCHEMA)
    db.close()
    led = Ledger(p)
    assert "trail" in {r[1] for r in led.db.execute("PRAGMA table_info(positions)")}


# ---------------------------------------------------------------- learning and readiness
def _fake_record(led, n_sessions, pnl_per_trade, trades_per_session=2):
    led.open_account(500, 10.0, 0.25, {"name": "orb", "params": {}})
    eq = led.cash()
    for k in range(n_sessions):
        day = (pd.Timestamp("2026-01-05") + pd.Timedelta(days=k)).date().isoformat()
        led.start_session(day, "training", eq, 10.0, [])
        for j in range(trades_per_session):
            p = pnl_per_trade[(k * trades_per_session + j) % len(pnl_per_trade)]
            led.db.execute("INSERT INTO trades (day, symbol, qty, entry_price, exit_price, net_pnl, costs) VALUES (?,?,?,?,?,?,?)",
                           (day, "AAA", 1, 5.0, 5.0 + p, p, 0.02))
            eq += p
        led.mark_session(day, "training", "completed", end_equity_usd=eq)


def test_readiness_not_ready_with_short_record(tmp_path):
    from papertrader import readiness
    led = Ledger(tmp_path / "r.sqlite"); led.quiet = True
    _fake_record(led, 10, [0.3, -0.1])
    res = readiness.assess(led)
    assert not res["ready"]
    assert "NOT READY" in readiness.markdown(res)


def test_readiness_ready_only_with_long_profitable_stable_record(tmp_path):
    from papertrader import readiness
    led = Ledger(tmp_path / "r.sqlite"); led.quiet = True
    _fake_record(led, 70, [0.05, 0.04, -0.02, 0.06])
    assert readiness.assess(led)["ready"]
    led2 = Ledger(tmp_path / "r2.sqlite"); led2.quiet = True
    _fake_record(led2, 70, [0.05, -0.06])  # losing record
    assert not readiness.assess(led2)["ready"]


def test_weekly_review_only_switches_on_clear_improvement():
    from papertrader.review import decide
    cur = {"name": "orb", "params": {"a": 1}}
    def row(spec, i_net, o_net, i_tr=20, o_tr=8):
        return {"strategy": spec, "in_sample": {"net_pnl_usd": i_net, "trades": i_tr}, "out_of_sample": {"net_pnl_usd": o_net, "trades": o_tr}}
    better = {"name": "momentum_leaders", "params": {"b": 2}}
    rows = [row(cur, -1.0, -0.5), row(better, 0.5, 0.2), row({"name": "no_trade", "params": {}}, 0, 0, 0, 0)]
    assert decide(rows, cur, 50.0, evaluation_done=False)[0] is None      # never during the evaluation
    assert decide(rows, cur, 50.0, evaluation_done=True)[0] == better
    slight = [row(cur, 0.10, 0.05), row(better, 0.15, 0.06)]                # within the 0.5% margin
    assert decide(slight, cur, 50.0, evaluation_done=True)[0] is None
    worse_recent = [row(cur, -1.0, 0.5), row(better, 1.0, 0.1)]             # better overall, worse recently
    assert decide(worse_recent, cur, 50.0, evaluation_done=True)[0] is None


def test_archive_roundtrip(tmp_path):
    from papertrader import archive
    a = make_day("2026-10-15", 4.0, flat_path)
    archive.save_day(tmp_path, {"AAA": a}, date(2026, 10, 15))
    back = archive.load(tmp_path, NY)["AAA"]
    assert len(back) == len(a) and back.index[0] == a.index[0]
    assert back["Close"].iloc[10] == pytest.approx(a["Close"].iloc[10], rel=1e-5)


def test_market_filter_blocks_entries_when_spy_is_weak(cfg, cal, tmp_path):
    s = BuyAt(minute=20, stop_pct=0.01, target_pct=0.02)
    s.params["market_filter"] = True
    led, eng, w = setup_engine(cfg, cal, tmp_path, s)
    df = make_day("2026-10-15", 4.0, breakout_path)
    spy_down = compute_features(make_day("2026-10-15", 500.0, lambda i: 1 - 0.001 * i), w.open)
    eng.process(feats(df, w), market=spy_down)
    assert not led.orders()
    led2, eng2, w2 = setup_engine(cfg, cal, tmp_path / "b", BuyAt(minute=20, stop_pct=0.01, target_pct=0.02))
    eng2.strategy.params["market_filter"] = True
    spy_up = compute_features(make_day("2026-10-15", 500.0, lambda i: 1 + 0.001 * i), w2.open)
    eng2.process(feats(df, w2), market=spy_up)
    assert led2.orders()
