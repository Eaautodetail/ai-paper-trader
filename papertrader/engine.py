"""Session engine: the single code path used by both backtests and live paper trading.

It walks forward one completed 1-minute bar at a time and, for each bar:
  1. fills pending simulated orders (simulated broker, with a final 20% position check),
  2. checks resting stop and target exits of open positions,
  3. at or after the end of the window (11:30 New York): cancels pending entries and sells everything,
  4. updates equity and enforces the daily loss limit (halt + flatten),
  5. asks the strategy for signals and passes each through the independent RiskManager.
Progress (the last processed bar) is stored in the ledger, so a restarted run continues
where it stopped and never processes a bar, or places an order, twice.
"""
import math
from datetime import timedelta

import pandas as pd

from .costs import CostModel
from .ledger import Ledger
from .market_calendar import SessionWindow
from .risk import RiskContext, RiskManager
from .safety import LIVE_TRADING_ENABLED, SafetyError
from .strategies import Strategy

BAR = timedelta(minutes=1)


class SessionEngine:
    def __init__(self, ledger: Ledger, window: SessionWindow, strategy: Strategy, costs: CostModel,
                 risk: RiskManager, kind: str, entries_allowed_from: pd.Timestamp | None = None,
                 fx_usdsek: float | None = None):
        if LIVE_TRADING_ENABLED:
            raise SafetyError("live trading flag set")
        self.l, self.w, self.strategy, self.costs, self.risk, self.kind = ledger, window, strategy, costs, risk, kind
        self.day = window.day.isoformat()
        self.start = pd.Timestamp(window.start)
        self.end = pd.Timestamp(window.end)
        self.entries_allowed_from = pd.Timestamp(entries_allowed_from) if entries_allowed_from is not None else self.start
        self.fx = fx_usdsek
        self.last_close: dict[str, float] = {}
        s = self.l.session(self.day)
        self.last_bar = pd.Timestamp(s["last_bar"]) if s and s["last_bar"] else None
        self.halted = bool(s["halted"]) if s else False
        self.stop_requested = False
        self.changed = False  # set when something worth persisting happened

    # ---- helpers -----------------------------------------------------------------
    def equity(self) -> float:
        val = self.l.cash()
        for p in self.l.positions():
            val += p["qty"] * self.last_close.get(p["symbol"], p["avg_price"])
        return val

    def session_start_equity(self) -> float:
        s = self.l.session(self.day)
        return float(s["start_equity_usd"])

    def _today_orders(self):
        return self.l.orders(self.day)

    def flat(self) -> bool:
        return not self.l.positions() and not self.l.pending_orders(self.day)

    # ---- order handling ----------------------------------------------------------
    def _fill_pending(self, sym: str, t: pd.Timestamp, bar) -> None:
        for o in self.l.pending_orders(self.day):
            if o["symbol"] != sym or pd.Timestamp(o["submitted_at"]) > t:
                continue
            if o["side"] == "buy":
                if t >= self.end or self.halted or self.stop_requested:
                    self.l.cancel_order(o["id"], "window ended" if t >= self.end else "trading halted")
                    self.changed = True
                    continue
                price = self.costs.buy_price(float(bar.Open))
                qty = o["qty"]
                # Execution-engine guard: re-check the 20% limit and cash at the actual fill price.
                eq = self.equity()
                max_q = min(math.floor(self.risk.max_position_value(eq) / price),
                            math.floor(self.l.cash() / (price + self.costs.commission(1))))
                if max_q < qty:
                    self.l.log(self.day, "INFO", f"{sym}: fill-time check reduced qty {qty} -> {max(max_q, 0)} (20% / cash limit)")
                    qty = max_q
                if qty < 1:
                    self.l.cancel_order(o["id"], "exceeds limits at fill price")
                    self.changed = True
                    continue
                comm = self.costs.commission(qty)
                self.l.record_buy(o["id"], sym, qty, price, t.isoformat(), comm, (price - float(bar.Open)) * qty,
                                  o["stop"], o["target"], self.day, o["strategy"], o["trail"])
                self.l.log(self.day, "TRADE", f"BUY {qty} {sym} @ {price:.4f} (bar open {bar.Open:.4f}) stop {o['stop']:.4f} target {o['target']:.4f}")
            else:
                self._sell(o["id"], sym, o["qty"], self.costs.sell_price(float(bar.Open)), float(bar.Open), t, o["exit_kind"] or "market")
            self.changed = True

    def _sell(self, order_id, sym, qty, price, ref, t, kind):
        fees = self.costs.sell_fees(qty, price)
        comm = self.costs.commission(qty)
        self.l.record_sell(order_id, sym, qty, price, t.isoformat(), comm, fees, max(0.0, (ref - price) * qty), kind)
        self.l.log(self.day, "TRADE", f"SELL {qty} {sym} @ {price:.4f} ({kind}), fees {fees + comm:.2f} USD")
        self.changed = True

    def _exit_now(self, pos, t, price, ref, kind):
        key = f"{self.day}|exit|{pos['symbol']}|{pos['entry_time']}"
        oid = self.l.add_order(key, self.day, pos["symbol"], "sell", pos["qty"], t.isoformat(), pos["strategy"] or "", kind)
        if oid is None:  # already exited in an earlier run
            return
        self._sell(oid, pos["symbol"], pos["qty"], price, ref, t, kind)

    def _submit_flatten(self, t_submit: pd.Timestamp, kind: str):
        for p in self.l.positions():
            if p["day"] != self.day:
                continue
            key = f"{self.day}|exit|{p['symbol']}|{p['entry_time']}"
            oid = self.l.add_order(key, self.day, p["symbol"], "sell", p["qty"], t_submit.isoformat(), p["strategy"] or "", kind)
            if oid is not None:
                self.l.db.execute("UPDATE orders SET exit_kind = ? WHERE id = ?", (kind, oid))
                self.changed = True
        for o in self.l.pending_orders(self.day):
            if o["side"] == "buy":
                self.l.cancel_order(o["id"], kind)
                self.changed = True

    def _manage_position(self, p, t, bar):
        if pd.Timestamp(p["entry_time"]) > t:
            return
        if any(o["symbol"] == p["symbol"] and o["side"] == "sell" for o in self.l.pending_orders(self.day)):
            return
        if t >= self.end:
            self._exit_now(p, t, self.costs.sell_price(float(bar.Open)), float(bar.Open), "window_end")
            return
        if bar.Low <= p["stop"]:
            ref = min(p["stop"], float(bar.Open))
            self._exit_now(p, t, self.costs.stop_fill(p["stop"], float(bar.Open)), ref, "stop")
        elif pd.Timestamp(p["entry_time"]) < t and bar.High >= p["target"] + self.costs.half_spread(p["target"]):
            self._exit_now(p, t, float(p["target"]), float(p["target"]), "target")
        elif p["trail"] > 0:
            # Trailing stop: after this bar, the stop follows the highest price minus the trail.
            new_stop = float(bar.High) - p["trail"]
            if new_stop > p["stop"]:
                self.l.raise_stop(p["symbol"], new_stop)
                self.changed = True

    # ---- main step ---------------------------------------------------------------
    def process(self, frames: dict[str, pd.DataFrame], data_fresh: bool = True, now: pd.Timestamp | None = None) -> None:
        """frames: per symbol, feature frames holding only COMPLETED bars of this session day."""
        times = sorted({t for f in frames.values() for t in f.index if self.last_bar is None or t > self.last_bar})
        for t in times:
            self._step(t, frames, data_fresh)
            self.last_bar = t
            self.l.set_last_bar(self.day, t.isoformat())

    def _step(self, t, frames, data_fresh):
        for sym, f in frames.items():
            if t not in f.index:
                continue
            bar = f.loc[t]
            self._fill_pending(sym, t, bar)
            for p in self.l.positions():
                if p["symbol"] == sym:
                    self._manage_position(p, t, bar)
            self.last_close[sym] = float(bar.Close)

        eq = self.equity()
        if t.minute % 5 == 0:
            self.l.snapshot(self.day, eq, self.fx)
        start_eq = self.session_start_equity()
        pnl = eq - start_eq
        if not self.halted and pnl <= -self.risk.daily_loss_pct * start_eq:
            self.halted = True
            self.l.set_halted(self.day)
            self.l.log(self.day, "WARN", f"Daily loss limit hit (P&L {pnl:.2f} USD <= -{self.risk.daily_loss_pct:.0%} of {start_eq:.2f}); no new trades, closing positions")
            self._submit_flatten(t + BAR, "daily_loss_limit")
        if self.stop_requested:
            self._submit_flatten(t + BAR, "stop_requested")
            return

        submit = t + BAR  # an order is placed when the signal bar has closed
        if self.halted or not (self.start <= submit < self.end) or t < self.entries_allowed_from:
            return
        open_syms = {p["symbol"] for p in self.l.positions()}
        pending_syms = {o["symbol"] for o in self.l.pending_orders(self.day)}
        orders = self._today_orders()
        traded = {o["symbol"] for o in orders if o["side"] == "buy" and o["status"] in ("filled", "pending")}
        entries = sum(1 for o in orders if o["side"] == "buy" and o["status"] in ("filled", "pending"))
        signals = []
        for sym, f in frames.items():
            if t not in f.index:
                continue
            sig = self.strategy.signal(sym, f, f.index.get_loc(t))
            if sig is not None:
                signals.append(sig)
        for sig in sorted(signals, key=lambda s: -s.score):
            sym = sig.symbol
            ctx = RiskContext(equity=eq, cash=self.l.cash() - self._reserved_cash(), session_start_equity=start_eq,
                              session_pnl=pnl, open_symbols=open_syms, pending_symbols=pending_syms,
                              traded_symbols=traded, entries_today=entries, in_window=True,
                              data_fresh=data_fresh, halted=self.halted)
            d = self.risk.evaluate(sig, ctx)
            if not d.approved:
                self.l.log(self.day, "SKIP", f"{sym} {sig.strategy} signal rejected: {d.reason}")
                continue
            key = f"{self.day}|{sig.strategy}|{sym}|{sig.bar_time.isoformat()}"
            oid = self.l.add_order(key, self.day, sym, "buy", d.qty, submit.isoformat(), sig.strategy, sig.reason,
                                   sig.stop, sig.target, sig.trail)
            if oid is not None:
                self.l.log(self.day, "ORDER", f"BUY {d.qty} {sym} at next bar open (est {d.est_entry:.4f}); planned max loss {d.planned_loss:.3f} USD; {sig.reason}")
                pending_syms.add(sym)
                traded.add(sym)
                entries += 1
                self.changed = True

    def _reserved_cash(self) -> float:
        total = 0.0
        for o in self.l.pending_orders(self.day):
            if o["side"] == "buy":
                total += o["qty"] * self.costs.buy_price(self.last_close.get(o["symbol"], 0.0)) * 1.01
        return total

    def finalize_without_bars(self, t: pd.Timestamp) -> None:
        """Fallback if no bar at/after the window end ever arrives: sell at the last known close."""
        for p in self.l.positions():
            if p["day"] != self.day:
                continue
            ref = self.last_close.get(p["symbol"], p["avg_price"])
            self.l.log(self.day, "WARN", f"{p['symbol']}: no bar after window end; closing at last known price {ref:.4f}")
            self._exit_now(p, t, self.costs.sell_price(ref), ref, "window_end_fallback")
        for o in self.l.pending_orders(self.day):
            self.l.cancel_order(o["id"], "window ended")
