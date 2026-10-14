"""Independent risk manager. Every entry must pass these checks; strategies cannot bypass them.

Limits (from config.toml, enforced here in code):
* long only: no short selling, no margin/leverage (cash must cover the full purchase), no derivatives
* whole shares only
* position value <= 20% of current equity (checked again by the simulated broker at fill time)
* planned loss (entry -> stop, incl. exit costs and fees) <= 0.5% of current equity
* planned loss also must fit inside what is left of the daily loss limit
* daily loss limit: 2% of the session's starting equity -> halt and flatten (engine)
* only inside the trading window, only with fresh data, limited number of entries
"""
import math
from dataclasses import dataclass

from .costs import CostModel
from .safety import LIVE_TRADING_ENABLED
from .strategies import Signal


@dataclass
class Decision:
    approved: bool
    qty: int = 0
    reason: str = ""
    planned_loss: float = 0.0
    est_entry: float = 0.0


@dataclass
class RiskContext:
    equity: float               # current equity, USD
    cash: float                 # USD
    session_start_equity: float
    session_pnl: float          # realized + unrealized since session start, USD
    open_symbols: set
    pending_symbols: set
    traded_symbols: set         # symbols already entered this session
    entries_today: int
    in_window: bool
    data_fresh: bool
    halted: bool


class RiskManager:
    def __init__(self, cfg: dict, costs: CostModel):
        r = cfg["risk"]
        self.max_pos_pct = r["max_position_pct_equity"] / 100
        self.max_risk_pct = r["max_risk_per_trade_pct_equity"] / 100
        self.daily_loss_pct = r["daily_loss_limit_pct"] / 100
        self.max_open = r["max_open_positions"]
        self.max_entries = r["max_entries_per_session"]
        self.min_price = r["min_price_usd"]
        self.min_rr_cost = r["min_reward_to_cost"]
        self.costs = costs
        assert self.max_pos_pct <= 0.20 + 1e-12, "position limit may not exceed 20%"
        assert self.max_risk_pct <= 0.005 + 1e-12, "per-trade loss limit may not exceed 0.5%"
        assert self.daily_loss_pct <= 0.02 + 1e-12, "daily loss limit may not exceed 2%"

    def daily_limit_hit(self, ctx: RiskContext) -> bool:
        return ctx.session_pnl <= -self.daily_loss_pct * ctx.session_start_equity

    def max_position_value(self, equity: float) -> float:
        return self.max_pos_pct * equity

    def evaluate(self, sig: Signal, ctx: RiskContext) -> Decision:
        if LIVE_TRADING_ENABLED:
            return Decision(False, reason="live trading flag set")
        if ctx.halted or self.daily_limit_hit(ctx):
            return Decision(False, reason="daily loss limit reached")
        if not ctx.in_window:
            return Decision(False, reason="outside trading window")
        if not ctx.data_fresh:
            return Decision(False, reason="market data not fresh")
        if sig.symbol in ctx.open_symbols or sig.symbol in ctx.pending_symbols:
            return Decision(False, reason="already have a position or order in this symbol")
        if sig.symbol in ctx.traded_symbols:
            return Decision(False, reason="already traded this symbol this session")
        if ctx.entries_today >= self.max_entries:
            return Decision(False, reason="max entries per session reached")
        if len(ctx.open_symbols) + len(ctx.pending_symbols) >= self.max_open:
            return Decision(False, reason="max open positions reached")
        if not (sig.stop < sig.ref_price < sig.target):
            return Decision(False, reason="invalid stop/target (long only)")
        if sig.ref_price < self.min_price:
            return Decision(False, reason=f"price below {self.min_price} USD")

        entry = self.costs.buy_price(sig.ref_price)
        stop_exit = self.costs.sell_price(sig.stop)
        target_exit = sig.target
        loss_per_share = entry - stop_exit
        if loss_per_share <= 0:
            return Decision(False, reason="stop too close to cover costs")

        risk_budget = self.max_risk_pct * ctx.equity
        daily_room = self.daily_loss_pct * ctx.session_start_equity + min(0.0, ctx.session_pnl)
        budget = min(risk_budget, daily_room)

        q_pos = math.floor(self.max_position_value(ctx.equity) / entry)
        comm = self.costs.commission(1)
        q_cash = math.floor(ctx.cash / (entry + comm)) if ctx.cash > 0 else 0
        q = min(q_pos, q_cash)
        # largest whole-share quantity whose planned loss incl. all costs fits the budget
        while q >= 1:
            planned = q * loss_per_share + 2 * self.costs.commission(q) + self.costs.sell_fees(q, stop_exit)
            if planned <= budget + 1e-9:
                break
            q -= 1
        if q < 1:
            why = []
            if q_pos < 1:
                why.append(f"1 share ({entry:.2f} USD) exceeds the 20% position limit ({self.max_position_value(ctx.equity):.2f} USD)")
            if q_cash < 1:
                why.append("not enough cash")
            if not why:
                why.append(f"planned loss for 1 share exceeds the per-trade limit ({budget:.2f} USD)")
            return Decision(False, reason="; ".join(why))

        planned = q * loss_per_share + 2 * self.costs.commission(q) + self.costs.sell_fees(q, stop_exit)
        rt_cost = self.costs.round_trip_cost(q, sig.ref_price, target_exit)
        expected_gain = q * (target_exit - entry) - 2 * self.costs.commission(q) - self.costs.sell_fees(q, target_exit)
        if expected_gain < self.min_rr_cost * rt_cost:
            return Decision(False, reason=f"expected gain {expected_gain:.3f} USD is under {self.min_rr_cost:g}x costs {rt_cost:.3f} USD")
        return Decision(True, q, "ok", planned, entry)
