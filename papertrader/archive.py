"""Growing archive of 1-minute bars, saved after every session.

Yahoo only keeps about 30 days of 1-minute history. Saving each day's bars to
data/bars/ lets backtests and the weekly review learn from a longer and longer past.
"""
from pathlib import Path

import pandas as pd


def archive_dir(root: Path) -> Path:
    return root / "data" / "bars"


def save_day(root: Path, bars: dict[str, pd.DataFrame], day) -> Path | None:
    parts = [df.assign(symbol=s) for s, df in bars.items() if df is not None and len(df)]
    if not parts:
        return None
    df = pd.concat(parts)
    df = df[df.index.date == day]
    if df.empty:
        return None
    p = archive_dir(root) / f"{day.isoformat()}.csv.gz"
    p.parent.mkdir(parents=True, exist_ok=True)
    out = df[["symbol", "Open", "High", "Low", "Close", "Volume"]].copy()
    out.index.name = "time"
    out.to_csv(p, float_format="%.6g", compression="gzip")
    return p


def load(root: Path, tz) -> dict[str, pd.DataFrame]:
    frames: dict[str, list] = {}
    for p in sorted(archive_dir(root).glob("*.csv.gz")):
        df = pd.read_csv(p, index_col="time", compression="gzip")
        df.index = pd.to_datetime(df.index, utc=True).tz_convert(tz)
        for s, g in df.groupby("symbol"):
            frames.setdefault(s, []).append(g.drop(columns="symbol"))
    return {s: pd.concat(v).sort_index() for s, v in frames.items()}


def merge(a: dict[str, pd.DataFrame], b: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    out = {}
    for s in set(a) | set(b):
        parts = [d for d in (a.get(s), b.get(s)) if d is not None and len(d)]
        df = pd.concat(parts).sort_index()
        out[s] = df[~df.index.duplicated(keep="last")]
    return out
