"""WAD — Williams Accumulation/Distribution (cumulative true-range accumulation)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def wad(df: pd.DataFrame) -> pd.Series:
    """Williams A/D: cumulative gains measured from the true range high/low vs prior close."""
    close = df[CLOSE]
    prev = close.shift(1)
    move = np.where(
        close > prev,
        close - np.minimum(df[LOW], prev),
        np.where(close < prev, close - np.maximum(df[HIGH], prev), 0.0),
    )
    series = pd.Series(move, index=df.index)
    series.iloc[0] = 0.0  # no prior close on the first bar
    return series.cumsum()


@INDICATORS.register
class WilliamsAD(Indicator):
    """Williams Accumulation/Distribution.

    What: cumulative accumulation using true-range distances vs the prior close.
    Best settings: none (cumulative); WAD/price divergence flags reversals.
    Edge cases: unchanged close contributes 0; first bar seeds at 0.
    Parity: tulip ``wad`` (validated against the explicit formula).
    """

    spec = IndicatorSpec(
        name="wad",
        category="volume",
        aliases=("Williams Accumulation/Distribution",),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("wad",),
        references=("Larry Williams", "tulip wad"),
        doc="ref/ta_docs/volume/misc_volume.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return wad(df)
