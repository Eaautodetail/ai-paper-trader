"""Transaction-cost model: spread, slippage, commission and US regulatory fees.

Execution model (used identically in backtests and in live paper trading):
* Market orders fill at the OPEN of the first 1-minute bar that starts at or after the
  order time, moved against us by half the spread plus slippage.
* Stop exits trigger when a bar's low touches the stop. Fill = the lower of the stop and
  that bar's open (gaps make it worse), minus half spread and slippage.
* Target exits (limit sells) fill at the target price only if the bar's high reaches
  target + half spread. If stop and target are both touched in the same bar, the stop is
  assumed to have happened first (the pessimistic choice).
* At the end of the trading window all positions are sold at the open of the first bar at
  or after 11:30 New York time, with the same spread and slippage as any market order.
"""
import math


def _ceil_cent(x: float) -> float:
    return math.ceil(round(x * 100, 6)) / 100 if x > 0 else 0.0


class CostModel:
    def __init__(self, cfg: dict):
        c = cfg["costs"]
        self.comm_ps = c["commission_per_share_usd"]
        self.comm_min = c["commission_min_usd"]
        self.sec = c["sec_fee_per_million_usd"]
        self.taf_ps = c["taf_per_share_usd"]
        self.taf_max = c["taf_max_usd"]
        self.hs_bps = c["half_spread_bps"]
        self.hs_min = c["min_half_spread_usd"]
        self.slip_bps = c["slippage_bps"]

    def half_spread(self, price: float) -> float:
        return max(self.hs_min, price * self.hs_bps / 1e4)

    def slippage(self, price: float) -> float:
        return price * self.slip_bps / 1e4

    def buy_price(self, ref: float) -> float:
        return ref + self.half_spread(ref) + self.slippage(ref)

    def sell_price(self, ref: float) -> float:
        return max(0.01, ref - self.half_spread(ref) - self.slippage(ref))

    def stop_fill(self, stop: float, bar_open: float) -> float:
        return self.sell_price(min(stop, bar_open))

    def commission(self, qty: int) -> float:
        if qty <= 0:
            return 0.0
        return max(self.comm_min, self.comm_ps * qty)

    def sell_fees(self, qty: int, price: float) -> float:
        """Regulatory fees on a sale, each rounded up to the next cent like brokers do."""
        if qty <= 0:
            return 0.0
        sec = _ceil_cent(qty * price * self.sec / 1e6)
        taf = _ceil_cent(min(self.taf_max, qty * self.taf_ps))
        return sec + taf

    def round_trip_cost(self, qty: int, ref_entry: float, ref_exit: float) -> float:
        """Total modeled cost (spread + slippage + commissions + fees) of buying and selling."""
        spread_in = (self.buy_price(ref_entry) - ref_entry) * qty
        spread_out = (ref_exit - self.sell_price(ref_exit)) * qty
        return spread_in + spread_out + 2 * self.commission(qty) + self.sell_fees(qty, ref_exit)
