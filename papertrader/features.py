"""Indicators computed from one day's 1-minute bars. Every value at row i uses only rows <= i."""
import numpy as np
import pandas as pd

OPENING_RANGE_MINUTES = (5, 15, 30)


def compute_features(bars: pd.DataFrame, session_open=None) -> pd.DataFrame:
    """bars: index = bar start time (New York), columns Open High Low Close Volume, one day only.
    session_open: the exchange open time; defaults to the first bar's time."""
    df = bars.copy()
    session_open = pd.Timestamp(session_open) if session_open is not None else df.index[0]
    minutes = ((df.index - session_open).total_seconds() // 60).astype(int).to_numpy()
    vol = df["Volume"].clip(lower=0)
    typical = (df["High"] + df["Low"] + df["Close"]) / 3
    cum_vol = vol.cumsum()
    df["vwap"] = (typical * vol).cumsum() / cum_vol.replace(0, np.nan)
    df["vwap"] = df["vwap"].fillna(df["Close"])
    df["ema9"] = df["Close"].ewm(span=9, adjust=False).mean()
    df["ema21"] = df["Close"].ewm(span=21, adjust=False).mean()
    prev_close = df["Close"].shift(1).fillna(df["Open"])
    tr = pd.concat([df["High"] - df["Low"], (df["High"] - prev_close).abs(), (df["Low"] - prev_close).abs()], axis=1).max(axis=1)
    df["atr"] = tr.rolling(14, min_periods=5).mean().bfill()
    df["ret15"] = df["Close"] / df["Close"].shift(15) - 1
    df["ret30"] = df["Close"] / df["Close"].shift(30) - 1
    df["rvol"] = vol / vol.rolling(30, min_periods=5).mean().shift(1)
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    df["rsi"] = (100 - 100 / (1 + rs)).fillna(50)
    for n in OPENING_RANGE_MINUTES:
        in_range = (minutes >= 0) & (minutes < n)
        hi = df["High"][in_range].max() if in_range.any() else np.nan
        lo = df["Low"][in_range].min() if in_range.any() else np.nan
        df[f"or{n}_high"] = np.where(minutes >= n, hi, np.nan)
        df[f"or{n}_low"] = np.where(minutes >= n, lo, np.nan)
    df["minute"] = minutes  # minutes since the first bar of the session
    return df
