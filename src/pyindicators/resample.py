"""Multi-timeframe helpers.

``resample_ohlcv`` aggregates a base-timeframe canonical OHLCV frame up to a higher
timeframe. ``align_to_base`` broadcasts a higher-timeframe (indicator) frame back onto a
base-timeframe index using a backward as-of merge on ``ts`` — so each base bar only ever
sees the most recent *fully-closed* higher-TF bar. That is the structural no-look-ahead
guarantee at the timeframe layer, mirroring ``BarContext`` at the row layer.

Registers nothing; imported harmlessly by the plugin autoloader.
"""

from __future__ import annotations

import pandas as pd

from .types import OHLCV_COLUMNS, Timeframe

# Coarse ordering (finest -> coarsest) used only to reject down-sampling.
_ORDER: dict[Timeframe, int] = {
    Timeframe.MIN1: 0,
    Timeframe.MIN5: 1,
    Timeframe.MIN15: 2,
    Timeframe.HOUR: 3,
    Timeframe.DAY: 4,
    Timeframe.WEEK: 5,
    Timeframe.MONTH: 6,
}

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
    """Aggregate a canonical OHLCV frame up to ``timeframe``.

    Args:
        df: canonical frame (integer index, ``ts`` UTC column, ``OHLCV_COLUMNS``).
        timeframe: the target (coarser) timeframe.
        base: the frame's own timeframe; if given, down-sampling is rejected.
        include_partial: keep the last, possibly still-forming, bucket. Default ``False``
            drops it so only closed bars are emitted (no look-ahead for screening "now").
    """
    if base is not None and _ORDER[timeframe] < _ORDER[base]:
        raise ValueError(f"cannot resample {base.value} up to a finer {timeframe.value}")
    if df.empty:
        return df.copy()

    indexed = df.set_index(pd.DatetimeIndex(df["ts"]))
    # Month buckets are conventionally left-labelled/closed; week/day/intraday right.
    if timeframe is Timeframe.MONTH:
        kw = {"label": "left", "closed": "left"}
    else:
        kw = {"label": "right", "closed": "right"}
    agg = {c: _AGG[c] for c in _AGG if c in indexed.columns}
    out = indexed.resample(timeframe.pandas_rule, **kw).agg(agg).dropna(subset=["open"])

    if not include_partial and not out.empty:
        last_base_ts = df["ts"].iloc[-1]
        # A bucket is closed once its label (its right/left boundary) is covered by data.
        out = out[out.index <= last_base_ts]

    out = out.reset_index(names="ts")
    return out[[c for c in OHLCV_COLUMNS if c in out.columns]]


def align_to_base(
    higher: pd.DataFrame,
    base: pd.DataFrame,
    *,
    prefix: str | None = None,
) -> pd.DataFrame:
    """Backward as-of merge of higher-TF columns onto the base-TF ``ts`` index.

    Each base row receives the most recent higher-TF row whose ``ts`` is ``<=`` it, so a
    not-yet-closed higher-TF bar is never visible. Non-``ts`` columns can be ``prefix``-ed
    (e.g. ``"wk"`` -> ``wk_sma_30``) to avoid collisions on the base frame.
    """
    if "ts" not in higher.columns or "ts" not in base.columns:
        raise ValueError("both frames must carry a 'ts' column for as-of alignment")
    right = higher.sort_values("ts").reset_index(drop=True)
    if prefix:
        right = right.rename(
            columns={c: f"{prefix}_{c}" for c in right.columns if c != "ts"}
        )
    left = base.sort_values("ts").reset_index(drop=True)
    merged = pd.merge_asof(left, right, on="ts", direction="backward", allow_exact_matches=True)
    merged.index = base.index
    return merged
