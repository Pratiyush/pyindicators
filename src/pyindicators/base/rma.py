"""RMA — Wilder's Smoothing / SMMA (base / overlap primitive).

Wilder's smoothing operator used inside RSI, ATR, and ADX/DMI: an EMA with
``alpha = 1/length`` (so much slower than a same-period EMA), seeded with the SMA of the
first ``length`` values. Getting this wrong (using a 2/(N+1) EMA instead) is the classic
"my RSI doesn't match TradingView" bug. See ``ref/ta_docs/base/RMA.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def rma(series: pd.Series, length: int) -> pd.Series:
    """Wilder's running moving average: ``alpha = 1/length``, SMA-seeded.

    Skips a leading prefix of NaNs (so it composes inside multi-stage indicators), seeding
    from the first ``length`` valid values; first valid output at index ``first+length-1``.
    """
    x = series.to_numpy(dtype="float64")
    n = x.size
    out = np.full(n, np.nan)
    nonnan = np.flatnonzero(~np.isnan(x))
    if nonnan.size >= length:
        f = int(nonnan[0])  # first valid index; warm-up NaNs are a leading prefix
        prev = x[f : f + length].mean()  # SMA seed
        out[f + length - 1] = prev
        for i in range(f + length, n):
            prev = (prev * (length - 1) + x[i]) / length
            out[i] = prev
    return pd.Series(out, index=series.index)


@INDICATORS.register
class RMA(Indicator):
    """Wilder's Smoothing (SMMA).

    What: Wilder's recursive average (alpha = 1/N); the smoother inside RSI/ATR/ADX.
    Best settings: ``length`` inherited from the parent indicator (14 for RSI/ATR/ADX).
    Edge cases: SMA seed; ADX needs ~150 bars before RMA-of-RMA stabilises.
    Parity: pandas-ta ``rma`` / tulip ``wilders``; matches TA-Lib's internal Wilder smoothing.
    """

    spec = IndicatorSpec(
        name="rma",
        category="base",
        aliases=("SMMA", "Wilder's Smoothing", "Modified MA", "Running MA"),
        inputs=(CLOSE,),
        outputs=("rma",),
        talib_compatible=True,
        references=("pandas-ta rma", "tulip wilders"),
        doc="ref/ta_docs/base/RMA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return rma(df[CLOSE], self.params["length"])
