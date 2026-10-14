"""Market data from Yahoo Finance through the open-source `yfinance` package (free, no key).

Yahoo is an unofficial source: it is free and has 1-minute US stock bars for the last
~30 days, but it has no service guarantee. Every session therefore checks that the feed is
current before trading and skips the session if it is not.
"""
import time
from datetime import datetime, timedelta

import pandas as pd

COLS = ["Open", "High", "Low", "Close", "Volume"]


def _yf():
    import yfinance as yf  # imported lazily so tests run without network
    return yf


def _split(raw: pd.DataFrame, symbols: list[str], tz) -> dict[str, pd.DataFrame]:
    out = {}
    if raw is None or raw.empty:
        return out
    for s in symbols:
        try:
            df = raw[s] if isinstance(raw.columns, pd.MultiIndex) else raw
        except KeyError:
            continue
        df = df[[c for c in COLS if c in df.columns]].dropna(subset=["Open", "High", "Low", "Close"])
        if df.empty:
            continue
        idx = df.index
        df.index = (idx.tz_localize("UTC") if idx.tz is None else idx).tz_convert(tz)
        df["Volume"] = df["Volume"].fillna(0)
        out[s] = df.sort_index()
    return out


def download(symbols: list[str], tz, retries: int = 3, **kw) -> dict[str, pd.DataFrame]:
    last_err = None
    for attempt in range(retries):
        try:
            raw = _yf().download(symbols, group_by="ticker", auto_adjust=False, prepost=False,
                                 progress=False, threads=True, **kw)
            return _split(raw, symbols, tz)
        except Exception as e:  # network hiccup or rate limit: back off and retry
            last_err = e
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"Yahoo download failed: {last_err}")


def intraday_today(symbols: list[str], tz, now: datetime) -> dict[str, pd.DataFrame]:
    """Today's completed 1-minute bars. The still-forming current minute is dropped."""
    data = download(symbols, tz, period="1d", interval="1m")
    cutoff = pd.Timestamp(now) - timedelta(seconds=60)
    today = pd.Timestamp(now).date()
    return {s: df[(df.index <= cutoff) & (df.index.date == today)] for s, df in data.items()}


def intraday_range(symbols: list[str], tz, start: datetime, end: datetime) -> dict[str, pd.DataFrame]:
    """1-minute bars between two dates, fetched in 7-day pieces (Yahoo's per-request limit)."""
    parts: dict[str, list] = {s: [] for s in symbols}
    cur = start
    while cur < end:
        nxt = min(cur + timedelta(days=7), end)
        chunk = download(symbols, tz, start=cur.strftime("%Y-%m-%d"), end=nxt.strftime("%Y-%m-%d"), interval="1m")
        for s, df in chunk.items():
            parts[s].append(df)
        cur = nxt
    return {s: pd.concat(v).sort_index().loc[lambda d: ~d.index.duplicated()] for s, v in parts.items() if v}


def daily(symbols: list[str], tz, period: str = "3mo") -> dict[str, pd.DataFrame]:
    return download(symbols, tz, period=period, interval="1d")


def usdsek(fx_symbol: str = "SEK=X") -> float:
    """Latest USD/SEK rate (SEK per 1 USD)."""
    df = _yf().download(fx_symbol, period="5d", interval="1d", progress=False, auto_adjust=False)
    if df is None or df.empty:
        raise RuntimeError("could not fetch USD/SEK")
    close = df["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    rate = float(close.dropna().iloc[-1])
    if not 5 < rate < 20:
        raise RuntimeError(f"implausible USD/SEK rate {rate}")
    return rate


def liquidity_table(daily_bars: dict[str, pd.DataFrame], before: pd.Timestamp, lookback: int = 20) -> pd.DataFrame:
    """Per symbol: last close and average daily dollar volume, using only days before `before`."""
    rows = []
    for s, df in daily_bars.items():
        d = df[df.index.normalize().tz_localize(None) < pd.Timestamp(before).tz_localize(None).normalize()].tail(lookback)
        if len(d) < 5:
            continue
        rows.append({"symbol": s, "last_close": float(d["Close"].iloc[-1]),
                     "avg_dollar_volume": float((d["Close"] * d["Volume"]).mean())})
    return pd.DataFrame(rows).set_index("symbol") if rows else pd.DataFrame(columns=["last_close", "avg_dollar_volume"])


def select_universe(liq: pd.DataFrame, cfg: dict, equity_usd: float, costs) -> list[str]:
    """Symbols where one whole share fits inside the 20% limit and liquidity is high enough."""
    r = cfg["risk"]
    cap = r["max_position_pct_equity"] / 100 * equity_usd
    ok = liq[(liq["avg_dollar_volume"] >= r["min_avg_daily_dollar_volume_usd"]) &
             (liq["last_close"] >= r["min_price_usd"]) &
             (liq["last_close"].map(costs.buy_price) <= cap * 0.97)]  # 3% headroom for the open
    return sorted(ok.index.tolist())
