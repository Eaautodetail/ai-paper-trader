"""Deterministic candidate strategies. All are long-only and look only at completed bars.

Each strategy returns a Signal (a proposal) or None. A signal is never an order: the
independent RiskManager decides whether, and how many whole shares, can be traded.
"""
from dataclasses import dataclass, field
import math

import pandas as pd


@dataclass(frozen=True)
class Signal:
    symbol: str
    bar_time: pd.Timestamp     # start time of the completed bar that produced the signal
    ref_price: float           # that bar's close
    stop: float
    target: float
    strategy: str
    reason: str
    trail: float = 0.0         # trailing-stop distance in USD (0 = fixed stop)
    score: float = 0.0         # when several stocks signal at once, higher scores are tried first


def _ok(*vals) -> bool:
    return all(v is not None and not (isinstance(v, float) and math.isnan(v)) for v in vals)


@dataclass
class Strategy:
    name: str = "base"
    params: dict = field(default_factory=dict)
    market: pd.DataFrame | None = None  # SPY feature frame, set by the engine each step

    def market_ok(self, t) -> bool:
        """With market_filter on, only buy while the whole market (SPY) trades above its VWAP."""
        if not self.params.get("market_filter"):
            return True
        m = self.market
        if m is None or m.empty or t < m.index[0]:
            return False
        r = m.loc[:t].iloc[-1]
        return bool(r.Close > r.vwap)

    def signal(self, symbol: str, f: pd.DataFrame, i: int) -> Signal | None:
        raise NotImplementedError

    def describe(self) -> dict:
        return {"name": self.name, "params": self.params}

    def with_market_filter(self) -> "Strategy":
        s = type(self)(**{k: v for k, v in self.params.items() if k != "market_filter"})
        s.params["market_filter"] = True
        return s


class NoTrade(Strategy):
    """Baseline: never trades. Any strategy must beat holding cash after costs."""
    def __init__(self, **_):
        super().__init__("no_trade", {})

    def signal(self, symbol, f, i):
        return None


class OpeningRangeBreakout(Strategy):
    """Buy when price closes above the first N minutes' high with above-average volume,
    while above VWAP. Stop under the range (capped by ATR), target = target_r x risk."""
    def __init__(self, or_minutes=15, rvol_min=1.5, target_r=2.0, stop_atr=2.0, last_entry_minute=90, market_filter=False):
        super().__init__("orb", dict(or_minutes=or_minutes, rvol_min=rvol_min, target_r=target_r,
                                     stop_atr=stop_atr, last_entry_minute=last_entry_minute))
        if market_filter:
            self.params["market_filter"] = True

    def signal(self, symbol, f, i):
        p = self.params
        if i < 1:
            return None
        r, prev = f.iloc[i], f.iloc[i - 1]
        n = p["or_minutes"]
        hi, lo = r.get(f"or{n}_high"), r.get(f"or{n}_low")
        if not _ok(hi, lo, r.atr, r.rvol, r.vwap) or r.minute > p["last_entry_minute"]:
            return None
        if not (r.Close > hi >= prev.Close and r.Close > r.vwap and r.rvol >= p["rvol_min"]):
            return None
        stop = max(lo, r.Close - p["stop_atr"] * r.atr)
        risk = r.Close - stop
        if risk <= 0:
            return None
        return Signal(symbol, f.index[i], float(r.Close), float(stop), float(r.Close + p["target_r"] * risk),
                      self.name, f"close {r.Close:.2f} broke {n}-min high {hi:.2f}, rvol {r.rvol:.1f}, above VWAP {r.vwap:.2f}")


class VwapTrendPullback(Strategy):
    """In an up-trend (EMA9 > EMA21, above VWAP, 30-min momentum), buy a green bar that
    dipped to the EMA9. Stop under EMA21 / bar low, target = target_r x risk."""
    def __init__(self, min_ret30=0.004, pull_atr=0.5, target_r=2.0, first_minute=30, last_entry_minute=100, market_filter=False):
        super().__init__("vwap_trend", dict(min_ret30=min_ret30, pull_atr=pull_atr, target_r=target_r,
                                            first_minute=first_minute, last_entry_minute=last_entry_minute))
        if market_filter:
            self.params["market_filter"] = True

    def signal(self, symbol, f, i):
        p = self.params
        r = f.iloc[i]
        if not _ok(r.atr, r.ret30, r.vwap) or not (p["first_minute"] <= r.minute <= p["last_entry_minute"]):
            return None
        trend = r.ema9 > r.ema21 and r.Close > r.vwap and r.ret30 >= p["min_ret30"]
        pulled = r.Low <= r.ema9 + p["pull_atr"] * r.atr and r.Close > r.Open and r.Close > r.ema9
        if not (trend and pulled):
            return None
        stop = min(r.Low, r.ema21) - 0.25 * r.atr
        risk = r.Close - stop
        if risk <= 0:
            return None
        return Signal(symbol, f.index[i], float(r.Close), float(stop), float(r.Close + p["target_r"] * risk),
                      self.name, f"uptrend (30-min {r.ret30:+.2%}), pullback to EMA9 {r.ema9:.2f}, above VWAP {r.vwap:.2f}")


class VwapReversion(Strategy):
    """Buy a sharp stretch below VWAP (in ATRs) with oversold RSI once a green bar appears.
    Target = VWAP, stop = bar low - stop_atr x ATR."""
    def __init__(self, dev_atr=3.0, rsi_max=25.0, stop_atr=1.0, first_minute=15, last_entry_minute=100, market_filter=False):
        super().__init__("vwap_reversion", dict(dev_atr=dev_atr, rsi_max=rsi_max, stop_atr=stop_atr,
                                                first_minute=first_minute, last_entry_minute=last_entry_minute))
        if market_filter:
            self.params["market_filter"] = True

    def signal(self, symbol, f, i):
        p = self.params
        r = f.iloc[i]
        if not _ok(r.atr, r.vwap, r.rsi) or not (p["first_minute"] <= r.minute <= p["last_entry_minute"]):
            return None
        if not (r.Close < r.vwap - p["dev_atr"] * r.atr and r.rsi <= p["rsi_max"] and r.Close > r.Open):
            return None
        stop = r.Low - p["stop_atr"] * r.atr
        if r.Close - stop <= 0 or r.vwap <= r.Close:
            return None
        return Signal(symbol, f.index[i], float(r.Close), float(stop), float(r.vwap),
                      self.name, f"{(r.vwap - r.Close) / r.atr:.1f} ATR below VWAP, RSI {r.rsi:.0f}")


class MomentumLeaders(Strategy):
    """Buy the morning's strongest risers: up at least `min_gain` since the open, above VWAP,
    in an up-trend, on heavy volume and at a new 10-minute high. When several stocks qualify at
    once the biggest riser is tried first. Exit with a trailing stop that follows the price up
    (trail_atr x ATR below the highest price), at +take_profit, or at 11:30 at the latest."""
    def __init__(self, min_gain=0.02, rvol_min=1.5, trail_atr=3.0, take_profit=0.05, first_minute=15,
                 last_entry_minute=75, market_filter=False):
        super().__init__("momentum_leaders", dict(min_gain=min_gain, rvol_min=rvol_min, trail_atr=trail_atr,
                                                  take_profit=take_profit, first_minute=first_minute,
                                                  last_entry_minute=last_entry_minute))
        if market_filter:
            self.params["market_filter"] = True

    def signal(self, symbol, f, i):
        p = self.params
        if i < 10:
            return None
        r = f.iloc[i]
        if not _ok(r.atr, r.vwap, r.rvol, r.ret_open) or not (p["first_minute"] <= r.minute <= p["last_entry_minute"]):
            return None
        prior_high = float(f["High"].iloc[i - 10:i].max())
        if not (r.ret_open >= p["min_gain"] and r.Close > r.vwap and r.ema9 > r.ema21
                and r.rvol >= p["rvol_min"] and r.Close >= prior_high):
            return None
        trail = p["trail_atr"] * float(r.atr)
        stop = float(r.Close) - trail
        if stop <= 0:
            return None
        return Signal(symbol, f.index[i], float(r.Close), stop, float(r.Close) * (1 + p["take_profit"]), self.name,
                      f"up {r.ret_open:+.1%} since the open, new 10-min high, rvol {r.rvol:.1f}, above VWAP {r.vwap:.2f}",
                      trail=trail, score=float(r.ret_open))


class RuleStrategy(Strategy):
    """A strategy assembled from fixed building blocks, so new ideas can be tried in the lab by
    writing a parameter set (strategy/lab.json) instead of new code. Every condition left out
    is not checked. All exits are the usual ones: stop, target, trailing stop, 11:30 deadline.

    Entry building blocks (on the completed 1-minute bar):
      first_minute / last_entry_minute  minutes after the open when buying is allowed
      min_gain / max_gain               stock's gain since the open (0.02 = 2%)
      rvol_min                          volume vs its recent average
      new_high_minutes                  close at or above the highest high of the previous N bars
      above_vwap                        close above VWAP
      max_vwap_atr                      at most this many ATRs above VWAP (avoids chasing)
      uptrend                           EMA9 above EMA21
      min_atr_pct / max_atr_pct         1-minute ATR as a % of price
      min_price / max_price             share price in USD
      spy_min_gain                      whole market (SPY) at least this much up since the open
      spy_above_vwap                    SPY above its VWAP
      rsi_max                           RSI at most this (for dip-buying ideas)
      below_vwap_atr                    at least this many ATRs BELOW VWAP (dip-buying)
    Exits: stop_atr (stop distance in ATRs), then either trail (trailing stop of the same
      distance) and/or target_r (target = risk x R) or take_profit (target in %).
    Ranking when several stocks signal at once: score = "gain", "rvol" or "dip".
    """
    def __init__(self, **params):
        p = {"first_minute": 15, "last_entry_minute": 90, "stop_atr": 2.0, "trail": False,
             "target_r": 2.0, "take_profit": None, "score": "gain"}
        p.update(params)
        super().__init__("rules", p)

    def _spy_ok(self, t) -> bool:
        p = self.params
        if p.get("spy_min_gain") is None and not p.get("spy_above_vwap"):
            return True
        m = self.market
        if m is None or m.empty or t < m.index[0]:
            return False
        r = m.loc[:t].iloc[-1]
        if p.get("spy_min_gain") is not None and not r.ret_open >= p["spy_min_gain"]:
            return False
        return not p.get("spy_above_vwap") or bool(r.Close > r.vwap)

    def signal(self, symbol, f, i):
        p = self.params
        if i < 10:
            return None
        r = f.iloc[i]
        if not _ok(r.atr, r.vwap, r.rvol, r.ret_open, r.rsi) or r.atr <= 0:
            return None
        if not (p["first_minute"] <= r.minute <= p["last_entry_minute"]):
            return None
        c = float(r.Close)
        checks = [
            p.get("min_gain") is None or r.ret_open >= p["min_gain"],
            p.get("max_gain") is None or r.ret_open <= p["max_gain"],
            p.get("rvol_min") is None or r.rvol >= p["rvol_min"],
            not p.get("above_vwap") or c > r.vwap,
            p.get("max_vwap_atr") is None or (c - r.vwap) / r.atr <= p["max_vwap_atr"],
            p.get("below_vwap_atr") is None or (r.vwap - c) / r.atr >= p["below_vwap_atr"],
            not p.get("uptrend") or r.ema9 > r.ema21,
            p.get("min_atr_pct") is None or 100 * r.atr / c >= p["min_atr_pct"],
            p.get("max_atr_pct") is None or 100 * r.atr / c <= p["max_atr_pct"],
            p.get("min_price") is None or c >= p["min_price"],
            p.get("max_price") is None or c <= p["max_price"],
            p.get("rsi_max") is None or r.rsi <= p["rsi_max"],
            not p.get("new_high_minutes") or c >= float(f["High"].iloc[max(0, i - int(p["new_high_minutes"])):i].max()),
        ]
        if not all(checks) or not self._spy_ok(f.index[i]):
            return None
        dist = p["stop_atr"] * float(r.atr)
        stop = c - dist
        if stop <= 0:
            return None
        if p.get("take_profit"):
            target = c * (1 + p["take_profit"])
        elif p.get("target_r"):
            target = c + p["target_r"] * dist
        else:
            target = c * 10  # no target: trailing stop or the deadline exits
        score = {"gain": float(r.ret_open), "rvol": float(r.rvol), "dip": float((r.vwap - c) / r.atr)}[p.get("score", "gain")]
        return Signal(symbol, f.index[i], c, stop, target, self.name,
                      f"rules: up {r.ret_open:+.1%} since open, rvol {r.rvol:.1f}, {(c - r.vwap) / r.atr:+.1f} ATR vs VWAP",
                      trail=dist if p.get("trail") else 0.0, score=score)


REGISTRY = {"no_trade": NoTrade, "orb": OpeningRangeBreakout, "vwap_trend": VwapTrendPullback,
            "vwap_reversion": VwapReversion, "momentum_leaders": MomentumLeaders, "rules": RuleStrategy}


def build(spec: dict) -> Strategy:
    return REGISTRY[spec["name"]](**spec.get("params", {}))


def candidate_grid() -> list[Strategy]:
    """The fixed set of strategy variants the backtest compares."""
    out: list[Strategy] = [NoTrade()]
    for n in (5, 15, 30):
        for tr in (1.5, 2.5):
            for rv in (1.2, 2.0):
                out.append(OpeningRangeBreakout(or_minutes=n, rvol_min=rv, target_r=tr))
    for m in (0.003, 0.006):
        for tr in (1.5, 2.5):
            out.append(VwapTrendPullback(min_ret30=m, target_r=tr))
    for d in (2.0, 3.0):
        for rs in (25.0, 35.0):
            out.append(VwapReversion(dev_atr=d, rsi_max=rs))
    out += momentum_grid()
    return out + [s.with_market_filter() for s in out if s.name in ("orb", "momentum_leaders")]


def momentum_grid() -> list[Strategy]:
    out: list[Strategy] = []
    for g in (0.015, 0.03):
        for tr in (2.0, 4.0):
            for tp in (0.03, 0.08):
                out.append(MomentumLeaders(min_gain=g, trail_atr=tr, take_profit=tp))
    return out
