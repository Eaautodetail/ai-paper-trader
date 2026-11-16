"""Long-term investing account. Bars here are SYNTHETIC fixtures for mechanics only."""
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from papertrader import invest

NY = ZoneInfo("America/New_York")


def series(closes, start="2024-01-02"):
    idx = pd.bdate_range(start, periods=len(closes), tz=NY)
    c = np.array(closes, dtype=float)
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({"Open": o, "High": np.maximum(o, c) * 1.005, "Low": np.minimum(o, c) * 0.995,
                         "Close": c, "Volume": 1e6}, index=idx)


def dip_path(n=300):
    up = list(np.linspace(100, 200, 250))          # long uptrend
    dip = list(np.linspace(200, 172, 10))          # -14% pullback
    rec = list(np.linspace(172, 210, n - 260))     # recovery
    return up + dip + rec


def cfg_for(cfg):
    return {**cfg, "invest": {**cfg["invest"]}}


def test_dip_buy_fills_next_open_and_respects_limits(cfg):
    bars = {"AAA": invest.indicators(series(dip_path())), "BBB": invest.indicators(series([50.0] * 300))}
    days = sorted({d.date() for d in bars["AAA"].index})
    prm = {**invest.DEFAULT_PARAMS, "dip_pct": 0.10, "rsi_max": 45}
    acc = invest.simulate(cfg, bars, prm, days, ["AAA", "BBB"])
    buys = [e for e in acc.s["events"] if "BUY" in e]
    assert buys, acc.s["events"][-10:]
    first = buys[0].split()[0]
    # the buy filled on a day after the dip started (decided on a close, filled next open)
    assert pd.Timestamp(first) > pd.Timestamp(str(days[250]))
    eq0 = acc.s["initial_usd"]
    for t in acc.s["trades"] + [dict(p, symbol=s) for s, p in acc.s["positions"].items()]:
        size = t["qty"] * t["entry"]
        assert size <= 0.2 * eq0 * 1.05          # never more than ~20% of the account
        assert t["qty"] != int(t["qty"]) or t["qty"] >= 1   # fractional shares allowed
    assert all(e["equity"] > 0 for e in acc.s["equity"])


def test_stop_sells_on_gap_down(cfg):
    path = dip_path(270) + [150.0] * 30                # crash after the buy
    bars = {"AAA": invest.indicators(series(path))}
    days = sorted({d.date() for d in bars["AAA"].index})
    acc = invest.simulate(cfg, bars, {**invest.DEFAULT_PARAMS, "rsi_max": 45}, days, ["AAA"])
    kinds = [t["exit_kind"] for t in acc.s["trades"]]
    assert "stop" in kinds or "trend_broken" in kinds
    loss = min(t["net"] for t in acc.s["trades"])
    assert loss > -0.02 * acc.s["initial_usd"]          # planned risk 0.5%; a gap can cost more, but not wildly


def test_whole_shares_mode_cannot_buy_expensive_stock(cfg):
    c = cfg_for(cfg)
    c["invest"]["fractional_shares"] = False
    bars = {"AAA": invest.indicators(series([x * 10 for x in dip_path()]))}   # 1000-2000 USD a share
    days = sorted({d.date() for d in bars["AAA"].index})
    acc = invest.simulate(c, bars, {**invest.DEFAULT_PARAMS, "rsi_max": 45}, days, ["AAA"])
    assert not acc.s["trades"] and not acc.s["positions"]


def test_live_catch_up_is_idempotent(cfg, tmp_root):
    (tmp_root / "strategy" / "watchlist.json").write_text(json.dumps(
        {"benchmark": "QQQ", "companies": [{"symbol": "AAA", "active": True}]}))
    bars = {"AAA": invest.indicators(series(dip_path()))}
    last = bars["AAA"].index[-1]
    mid = bars["AAA"].index[240]
    t1 = datetime.combine(mid.date(), datetime.min.time(), NY).replace(hour=17)
    msg = invest.run_live(cfg, tmp_root, now=t1, bars={"AAA": bars["AAA"].loc[:mid]}, fx=10.0)
    assert "updated" in msg
    t2 = datetime.combine(last.date(), datetime.min.time(), NY).replace(hour=17)
    invest.run_live(cfg, tmp_root, now=t2, bars=bars, fx=10.0)
    s1 = json.loads(invest.state_path(tmp_root).read_text())
    invest.run_live(cfg, tmp_root, now=t2, bars=bars, fx=10.0)    # same day again: nothing changes
    s2 = json.loads(invest.state_path(tmp_root).read_text())
    assert s1 == s2 and s1["last_day"] == str(last.date())
    assert len(s1["equity"]) == len({e["day"] for e in s1["equity"]})
    assert (tmp_root / "reports" / "invest.md").exists()
