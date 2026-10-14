"""Exchange calendar: which days are trading days and when the trading window is.

Uses the open-source `exchange_calendars` package (NYSE calendar "XNYS"), which includes
holidays and early closes. All exchange maths is done in America/New_York; Stockholm
times are only for display. Both zones' daylight-saving changes are handled by zoneinfo.
"""
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import exchange_calendars as xcals
import pandas as pd


@dataclass(frozen=True)
class SessionWindow:
    day: date
    open: datetime          # exchange open (tz-aware, New York)
    close: datetime         # exchange close for the day (may be early)
    start: datetime         # first moment new positions are allowed
    end: datetime           # trading window end: no new trades, flatten everything
    early_close: bool

    def display(self, tz: str) -> str:
        z = ZoneInfo(tz)
        return f"{self.start.astimezone(z):%Y-%m-%d %H:%M}-{self.end.astimezone(z):%H:%M} {tz}"


class MarketCalendar:
    def __init__(self, cfg: dict):
        s = cfg["schedule"]
        self.tz = ZoneInfo(s["exchange_timezone"])
        self.display_tz = s["display_timezone"]
        self.cal = xcals.get_calendar(s["exchange"])
        self.start_t = time.fromisoformat(s["session_start"])
        self.end_t = time.fromisoformat(s["session_end"])

    def is_trading_day(self, d: date) -> bool:
        return bool(self.cal.is_session(pd.Timestamp(d)))

    def window(self, d: date) -> SessionWindow | None:
        if not self.is_trading_day(d):
            return None
        ts = pd.Timestamp(d)
        open_ = self.cal.session_open(ts).to_pydatetime().astimezone(self.tz)
        close = self.cal.session_close(ts).to_pydatetime().astimezone(self.tz)
        start = max(open_, datetime.combine(d, self.start_t, self.tz))
        end = min(close, datetime.combine(d, self.end_t, self.tz))
        early = close.time() < time(16, 0)
        return SessionWindow(d, open_, close, start, end, early)

    def next_window(self, after: datetime) -> SessionWindow:
        d = after.astimezone(self.tz).date()
        for i in range(0, 15):
            w = self.window(d + timedelta(days=i))
            if w and w.end > after:
                return w
        raise RuntimeError("No trading session found in the next 15 days")

    def now(self) -> datetime:
        return datetime.now(self.tz)
