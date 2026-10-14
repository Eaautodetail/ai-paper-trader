"""Test helpers. The bars below are SYNTHETIC test fixtures, used only to check the
mechanics of the engine. They are never used for strategy evaluation or reports."""
import copy
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from papertrader.config import load_config
from papertrader.market_calendar import MarketCalendar


@pytest.fixture
def cfg():
    return load_config()


@pytest.fixture
def cal(cfg):
    return MarketCalendar(cfg)


def make_day(day: str, base: float, path, tz="America/New_York", start="09:30", minutes=150, vol=50_000) -> pd.DataFrame:
    """path: function minute -> price multiplier."""
    idx = pd.date_range(pd.Timestamp(f"{day} {start}", tz=tz), periods=minutes, freq="1min")
    closes = np.array([base * path(i) for i in range(minutes)])
    opens = np.concatenate([[closes[0]], closes[:-1]])
    highs = np.maximum(opens, closes) * 1.001
    lows = np.minimum(opens, closes) * 0.999
    vols = np.full(minutes, vol, dtype=float)
    return pd.DataFrame({"Open": opens, "High": highs, "Low": lows, "Close": closes, "Volume": vols}, index=idx)


def breakout_path(i):
    # flat range for 20 minutes, then a steady rise
    if i < 20:
        return 1.0 + 0.001 * ((i % 4) - 1.5)
    return 1.0 + 0.0015 * (i - 19)


def flat_path(i):
    return 1.0 + 0.0005 * ((i % 6) - 2.5)


class FakeClock:
    def __init__(self, t: datetime):
        self.t = t

    def now(self):
        return self.t

    def sleep(self, s):
        self.t = self.t + timedelta(seconds=s)


class FakeFeed:
    def __init__(self, days: dict, fx=10.0, daily=None, fail=False):
        self.days, self.fx, self._daily, self.fail = days, fx, daily, fail

    def _all(self, sym):
        parts = [d[sym] for d in self.days.values() if sym in d]
        return pd.concat(parts).sort_index() if parts else None

    def intraday(self, symbols, now):
        if self.fail:
            return {}
        out = {}
        for s in symbols:
            df = self._all(s)
            if df is None:
                continue
            cut = pd.Timestamp(now) - pd.Timedelta(seconds=60)
            df = df[(df.index <= cut) & (df.index.date == pd.Timestamp(now).date())]
            out[s] = df
        return out

    def bars_for_day(self, symbols, day):
        return {s: df[df.index.date == day] for s in symbols if (df := self._all(s)) is not None}

    def daily(self, symbols):
        idx = pd.date_range("2026-08-01", "2026-12-31", freq="B", tz="America/New_York")
        return {s: pd.DataFrame({"Open": 5.0, "High": 5.1, "Low": 4.9, "Close": 5.0, "Volume": 10_000_000}, index=idx)
                for s in symbols}

    def usdsek(self):
        return self.fx


@pytest.fixture
def tmp_root(tmp_path):
    (tmp_path / "control").mkdir()
    (tmp_path / "strategy").mkdir()
    return tmp_path


def small_universe_cfg(cfg, symbols=("AAA", "BBB")):
    c = copy.deepcopy(cfg)
    c["universe"]["symbols"] = list(symbols)
    return c
