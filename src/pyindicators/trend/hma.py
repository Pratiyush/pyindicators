"""HMA — Hull Moving Average (very low-lag, Alan Hull 2005).

``HMA(N) = WMA( 2*WMA(price, N/2) - WMA(price, N), round(sqrt(N)) )``. The WMA base is
essential — using EMA breaks the lag-cancelling property. Composes ``base.wma``.
See ``ref/ta_docs/trend/HMA.md``.
"""

from __future__ import annotations

import math

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import wma
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def hma(close: pd.Series, length: int = 16) -> pd.Series:
    """Hull Moving Average: WMA of (2*WMA(N/2) - WMA(N)) over round(sqrt(N))."""
    half = length // 2
    sqrt_len = int(round(math.sqrt(length)))
    return wma(2.0 * wma(close, half) - wma(close, length), sqrt_len)


@INDICATORS.register
class HMA(Indicator):
    """Hull Moving Average.

    What: a smooth, very responsive MA from weighted MAs that cancel lag.
    Best settings: ``length`` 16 (9 fast, 49-55 trend-following).
    Edge cases: warm-up ~ length + round(sqrt(length)); can briefly overshoot price.
    Parity: pandas-ta ``hma`` (not in core TA-Lib).
    """

    spec = IndicatorSpec(
        name="hma",
        category="trend",
        aliases=("Hull Moving Average",),
        inputs=(CLOSE,),
        outputs=("hma",),
        references=("Hull 2005", "pandas-ta hma"),
        doc="ref/ta_docs/trend/HMA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=16, ge=2)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return hma(df[CLOSE], self.params["length"])
