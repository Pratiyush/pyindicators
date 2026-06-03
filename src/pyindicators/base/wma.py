"""WMA — Weighted Moving Average / Linearly Weighted MA (base / overlap primitive).

Weights decline linearly from ``length`` (most recent) to 1 (oldest), divided by the
triangular number ``length*(length+1)/2``. The core component of HMA. See
``ref/ta_docs/base/WMA.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def wma(series: pd.Series, length: int) -> pd.Series:
    """Linearly weighted moving average (most-recent bar weighted ``length``)."""
    weights = np.arange(1, length + 1, dtype="float64")
    denom = weights.sum()
    return series.rolling(length, min_periods=length).apply(
        lambda w: np.dot(w, weights) / denom, raw=True
    )


@INDICATORS.register
class WMA(Indicator):
    """Weighted Moving Average.

    What: linearly weighted mean — less lag than SMA, less smooth than EMA at equal N.
    Best settings: ``length`` 9 or 20; WMA(length) is the building block of HMA.
    Edge cases: first ``length-1`` bars NaN; denominator is constant (never zero for N>=1).
    Parity: exact vs TA-Lib ``WMA`` / pandas-ta ``wma``.
    """

    spec = IndicatorSpec(
        name="wma",
        category="base",
        aliases=("Linearly Weighted MA", "LWMA"),
        inputs=(CLOSE,),
        outputs=("wma",),
        talib_compatible=True,
        references=("TA-Lib WMA", "pandas-ta wma", "tulip wma"),
        doc="ref/ta_docs/base/WMA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return wma(df[CLOSE], self.params["length"])
