"""Multi-timeframe helpers — resample OHLCV up, align higher-TF columns back down.

``resample_ohlcv`` aggregates a canonical OHLCV frame up to a coarser timeframe
(open=first, high=max, low=min, close=last, volume=sum). ``align_to_base`` broadcasts a
higher-timeframe frame back onto a base-timeframe ``ts`` index with a backward as-of merge,
so each base bar only ever sees the most recent *fully-closed* higher-TF bar — the
structural no-look-ahead guarantee at the timeframe layer (mirrors a point-in-time window
at the row layer). Kept as its own module so the MTF concern stays isolated.
"""

from __future__ import annotations

import pandas as pd

from .timeframe import Timeframe

# Coarse ordering (finest -> coarsest); used only to reject down-sampling.
_ORDER: dict[Timeframe, int] = {
    Timeframe.MIN1: 0,
    Timeframe.MIN5: 1,
    Timeframe.MIN15: 2,
    Timeframe.HOUR: 3,
    Timeframe.DAY: 4,
    Timeframe.WEEK: 5,
    Timeframe.MONTH: 6,
}

# How each canonical column aggregates into a coarser bar.
_AGG = {
    "open": "first",
    "high": "max",
    "low": "min",
    "close": "last",
    "close_raw": "last",
    "volume": "sum",
    "adj_factor": "last",
}


def resample_ohlcv(
    df: pd.DataFrame,
    timeframe: Timeframe,
    *,
    base: Timeframe | None = None,
    include_partial: bool = False,
) -> pd.DataFrame:
    """Aggregate a canonical OHLCV frame up to a coarser ``timeframe``.

    ``df`` carries a ``ts`` (UTC datetime) column, or is indexed by a ``DatetimeIndex``.
    ``close_raw`` / ``adj_factor`` (if present) carry their last value. With
    ``include_partial=False`` (default) the final, still-forming bucket is dropped so only
    closed bars are emitted (no look-ahead). ``base`` (the frame's own timeframe) rejects
    down-sampling. Returns a frame with a fresh ``ts`` column + the aggregated columns.
    """
    if base is not None and _ORDER[timeframe] < _ORDER[base]:
        raise ValueError(f"cannot resample {base.value} up to a finer {timeframe.value}")
    if df.empty:
        return df.copy()

    ts = df["ts"] if "ts" in df.columns else df.index.to_series()
    indexed = df.set_index(pd.DatetimeIndex(ts))
    # Month buckets are conventionally left-labelled/closed; week/day/intraday right.
    if timeframe is Timeframe.MONTH:
        kw = {"label": "left", "closed": "left"}
    else:
        kw = {"label": "right", "closed": "right"}
    agg = {c: _AGG[c] for c in _AGG if c in indexed.columns}
    out = indexed.resample(timeframe.pandas_rule, **kw).agg(agg).dropna(subset=["open"])

    if not include_partial and not out.empty:
        out = out[out.index <= pd.Timestamp(ts.iloc[-1])]

    return out.reset_index(names="ts")


def align_to_base(
    higher: pd.DataFrame,
    base: pd.DataFrame,
    *,
    prefix: str | None = None,
) -> pd.DataFrame:
    """Backward as-of merge of higher-TF columns onto the base-TF ``ts`` index.

    Each base row receives the most recent higher-TF row whose ``ts`` is ``<=`` it, so a
    not-yet-closed higher-TF bar is never visible (pair with ``include_partial=False``).
    Non-``ts`` higher columns can be ``prefix``-ed (``"wk"`` -> ``wk_sma_50``).
    """
    if "ts" not in higher.columns or "ts" not in base.columns:
        raise ValueError("both frames must carry a 'ts' column for as-of alignment")
    right = higher.sort_values("ts").reset_index(drop=True)
    if prefix:
        right = right.rename(columns={c: f"{prefix}_{c}" for c in right.columns if c != "ts"})
    left = base.sort_values("ts").reset_index(drop=True)
    merged = pd.merge_asof(left, right, on="ts", direction="backward", allow_exact_matches=True)
    merged.index = base.index
    return merged
