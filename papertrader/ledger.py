"""Persistent simulated ledger (SQLite file committed to the repository after every change).

Holds the starting capital, cash, positions, every order and fill with its costs, the
equity snapshots and an event log. Orders carry a unique idempotency key
(date|strategy|symbol|signal bar), so a restarted run can never place the same trade twice.
"""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS account (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  initial_sek REAL NOT NULL, fx_usdsek_initial REAL NOT NULL, fx_fee_sek REAL NOT NULL,
  initial_usd REAL NOT NULL, cash_usd REAL NOT NULL, created_at TEXT NOT NULL,
  strategy_json TEXT
);
CREATE TABLE IF NOT EXISTS sessions (
  day TEXT PRIMARY KEY, kind TEXT NOT NULL, status TEXT NOT NULL,
  start_equity_usd REAL, end_equity_usd REAL, fx_usdsek REAL,
  last_bar TEXT, halted INTEGER NOT NULL DEFAULT 0, note TEXT,
  started_at TEXT, finished_at TEXT, universe_json TEXT
);
CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT UNIQUE NOT NULL, day TEXT NOT NULL,
  symbol TEXT NOT NULL, side TEXT NOT NULL CHECK (side IN ('buy','sell')), qty INTEGER NOT NULL CHECK (qty > 0),
  submitted_at TEXT NOT NULL, status TEXT NOT NULL, strategy TEXT, reason TEXT,
  stop REAL, target REAL, fill_time TEXT, fill_price REAL, commission REAL DEFAULT 0,
  fees REAL DEFAULT 0, spread_cost REAL DEFAULT 0, exit_kind TEXT
);
CREATE TABLE IF NOT EXISTS positions (
  symbol TEXT PRIMARY KEY, qty INTEGER NOT NULL CHECK (qty > 0), avg_price REAL NOT NULL,
  entry_time TEXT NOT NULL, stop REAL NOT NULL, target REAL NOT NULL, day TEXT NOT NULL,
  entry_cost REAL NOT NULL DEFAULT 0, strategy TEXT
);
CREATE TABLE IF NOT EXISTS trades (
  id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT NOT NULL, symbol TEXT NOT NULL, qty INTEGER NOT NULL,
  entry_time TEXT, entry_price REAL, exit_time TEXT, exit_price REAL, exit_kind TEXT,
  gross_pnl REAL, costs REAL, net_pnl REAL, strategy TEXT
);
CREATE TABLE IF NOT EXISTS equity (
  ts TEXT NOT NULL, day TEXT NOT NULL, equity_usd REAL NOT NULL, cash_usd REAL NOT NULL, fx_usdsek REAL
);
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, day TEXT, level TEXT NOT NULL, message TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Ledger:
    def __init__(self, path: Path | str):
        self.path = Path(path) if str(path) != ":memory:" else None
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path or ":memory:", isolation_level=None)
        self.quiet = False
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=DELETE")
        self.db.executescript(SCHEMA)

    def close(self):
        self.db.close()

    # ---- account -------------------------------------------------------------
    def account(self):
        return self.db.execute("SELECT * FROM account WHERE id = 1").fetchone()

    def open_account(self, initial_sek: float, usdsek: float, fx_fee_pct: float, strategy: dict) -> None:
        """Create the account once. Calling it again never resets anything."""
        if self.account() is not None:
            return
        fee_sek = initial_sek * fx_fee_pct / 100
        usd = round((initial_sek - fee_sek) / usdsek, 6)
        self.db.execute("INSERT INTO account VALUES (1, ?, ?, ?, ?, ?, ?, ?)",
                        (initial_sek, usdsek, fee_sek, usd, usd, _now(), json.dumps(strategy)))
        self.log(None, "INFO", f"Account opened: {initial_sek:.2f} SEK at USD/SEK {usdsek:.4f}, "
                               f"conversion fee {fee_sek:.2f} SEK -> {usd:.2f} USD cash")

    def cash(self) -> float:
        return float(self.account()["cash_usd"])

    def strategy_spec(self) -> dict | None:
        a = self.account()
        return json.loads(a["strategy_json"]) if a and a["strategy_json"] else None

    # ---- sessions ------------------------------------------------------------
    def session(self, day: str):
        return self.db.execute("SELECT * FROM sessions WHERE day = ?", (day,)).fetchone()

    def sessions(self, kind: str | None = None):
        q, a = "SELECT * FROM sessions", ()
        if kind:
            q, a = q + " WHERE kind = ?", (kind,)
        return self.db.execute(q + " ORDER BY day", a).fetchall()

    def completed_sessions(self, kind: str) -> int:
        return self.db.execute("SELECT COUNT(*) FROM sessions WHERE kind = ? AND status = 'completed'",
                               (kind,)).fetchone()[0]

    def start_session(self, day: str, kind: str, start_equity: float, fx: float, universe: list[str]):
        if self.session(day) is None:
            self.db.execute("INSERT INTO sessions (day, kind, status, start_equity_usd, fx_usdsek, started_at, universe_json)"
                            " VALUES (?, ?, 'running', ?, ?, ?, ?)", (day, kind, start_equity, fx, _now(), json.dumps(universe)))
        else:
            self.db.execute("UPDATE sessions SET status = 'running' WHERE day = ? AND status = 'running'", (day,))

    def mark_session(self, day: str, kind: str, status: str, note: str = "", **cols):
        if self.session(day) is None:
            self.db.execute("INSERT INTO sessions (day, kind, status, started_at) VALUES (?, ?, ?, ?)",
                            (day, kind, status, _now()))
        sets = ["status = ?", "note = COALESCE(NULLIF(?, ''), note)"]
        vals = [status, note]
        for k, v in cols.items():
            sets.append(f"{k} = ?")
            vals.append(v)
        if status in ("completed", "skipped", "stopped"):
            sets.append("finished_at = ?")
            vals.append(_now())
        self.db.execute(f"UPDATE sessions SET {', '.join(sets)} WHERE day = ?", (*vals, day))

    def set_last_bar(self, day: str, ts: str):
        self.db.execute("UPDATE sessions SET last_bar = ? WHERE day = ?", (ts, day))

    def set_halted(self, day: str):
        self.db.execute("UPDATE sessions SET halted = 1 WHERE day = ?", (day,))

    # ---- orders and fills -----------------------------------------------------
    def add_order(self, key: str, day: str, symbol: str, side: str, qty: int, submitted_at: str,
                  strategy: str = "", reason: str = "", stop: float | None = None,
                  target: float | None = None) -> int | None:
        """Returns the new order id, or None if an order with this key already exists."""
        try:
            cur = self.db.execute(
                "INSERT INTO orders (key, day, symbol, side, qty, submitted_at, status, strategy, reason, stop, target)"
                " VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?)",
                (key, day, symbol, side, qty, submitted_at, strategy, reason, stop, target))
            return cur.lastrowid
        except sqlite3.IntegrityError:
            return None

    def pending_orders(self, day: str | None = None):
        q, a = "SELECT * FROM orders WHERE status = 'pending'", ()
        if day:
            q, a = q + " AND day = ?", (day,)
        return self.db.execute(q + " ORDER BY id", a).fetchall()

    def orders(self, day: str | None = None):
        q, a = "SELECT * FROM orders", ()
        if day:
            q, a = q + " WHERE day = ?", (day,)
        return self.db.execute(q + " ORDER BY id", a).fetchall()

    def cancel_order(self, order_id: int, why: str):
        self.db.execute("UPDATE orders SET status = 'cancelled', reason = reason || ' | cancelled: ' || ? "
                        "WHERE id = ? AND status = 'pending'", (why, order_id))

    def record_buy(self, order_id: int, symbol: str, qty: int, price: float, fill_time: str, commission: float,
                   spread_cost: float, stop: float, target: float, day: str, strategy: str):
        cost = qty * price + commission
        with self.db:
            self.db.execute("BEGIN")
            if self.cash() + 1e-9 < cost:
                raise ValueError("insufficient simulated cash")
            if self.db.execute("SELECT 1 FROM positions WHERE symbol = ?", (symbol,)).fetchone():
                raise ValueError("position already open")
            self.db.execute("UPDATE orders SET status='filled', fill_time=?, fill_price=?, commission=?, spread_cost=? WHERE id=?",
                            (fill_time, price, commission, spread_cost, order_id))
            self.db.execute("UPDATE account SET cash_usd = cash_usd - ? WHERE id = 1", (cost,))
            self.db.execute("INSERT INTO positions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (symbol, qty, price, fill_time, stop, target, day, commission + spread_cost, strategy))

    def record_sell(self, order_id: int, symbol: str, qty: int, price: float, fill_time: str, commission: float,
                    fees: float, spread_cost: float, exit_kind: str):
        with self.db:
            self.db.execute("BEGIN")
            pos = self.db.execute("SELECT * FROM positions WHERE symbol = ?", (symbol,)).fetchone()
            if pos is None or pos["qty"] < qty:
                raise ValueError("cannot sell more than held (no short selling)")
            self.db.execute("UPDATE orders SET status='filled', fill_time=?, fill_price=?, commission=?, fees=?, spread_cost=?, exit_kind=? WHERE id=?",
                            (fill_time, price, commission, fees, spread_cost, exit_kind, order_id))
            self.db.execute("UPDATE account SET cash_usd = cash_usd + ? WHERE id = 1", (qty * price - commission - fees,))
            buy = self.db.execute("SELECT commission, spread_cost FROM orders WHERE symbol=? AND side='buy' AND status='filled' "
                                  "ORDER BY id DESC LIMIT 1", (symbol,)).fetchone()
            entry_costs = (buy["commission"] + buy["spread_cost"]) if buy else 0.0
            gross = (price - pos["avg_price"]) * qty
            costs = entry_costs + commission + fees + spread_cost
            net = gross - (buy["commission"] if buy else 0.0) - commission - fees
            self.db.execute("INSERT INTO trades (day, symbol, qty, entry_time, entry_price, exit_time, exit_price, exit_kind,"
                            " gross_pnl, costs, net_pnl, strategy) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                            (pos["day"], symbol, qty, pos["entry_time"], pos["avg_price"], fill_time, price, exit_kind,
                             gross, costs, net, pos["strategy"]))
            if pos["qty"] == qty:
                self.db.execute("DELETE FROM positions WHERE symbol = ?", (symbol,))
            else:
                self.db.execute("UPDATE positions SET qty = qty - ? WHERE symbol = ?", (qty, symbol))

    def positions(self):
        return self.db.execute("SELECT * FROM positions ORDER BY symbol").fetchall()

    def trades(self, day: str | None = None):
        q, a = "SELECT * FROM trades", ()
        if day:
            q, a = q + " WHERE day = ?", (day,)
        return self.db.execute(q + " ORDER BY id", a).fetchall()

    # ---- equity and events ----------------------------------------------------
    def snapshot(self, day: str, equity: float, fx: float | None):
        self.db.execute("INSERT INTO equity VALUES (?, ?, ?, ?, ?)", (_now(), day, equity, self.cash(), fx))

    def log(self, day: str | None, level: str, message: str):
        self.db.execute("INSERT INTO events (ts, day, level, message) VALUES (?, ?, ?, ?)", (_now(), day, level, message))
        if not self.quiet:
            print(f"[{level}] {day or ''} {message}", flush=True)

    def events(self, day: str | None = None, limit: int = 500):
        q, a = "SELECT * FROM events", ()
        if day:
            q, a = q + " WHERE day = ?", (day,)
        return self.db.execute(q + " ORDER BY id DESC LIMIT ?", (*a, limit)).fetchall()
