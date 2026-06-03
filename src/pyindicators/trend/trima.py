"""TRIMA — Triangular Moving Average (overlap).

A double-SMA that weights the middle of the window most. TA-Lib's two-stage lengths differ
for odd vs even ``length``: odd -> SMA(SMA(x, (N+1)/2), (N+1)/2); even -> SMA(SMA(x, N/2+1),
N/2). Composes ``base.sma``. See ``ref/ta_docs/trend/misc_MA.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def trima(close: pd.Series, length: int = 20) -> pd.Series:
    """Triangular MA = SMA of SMA (TA-Lib odd/even two-stage lengths)."""
    if length % 2 == 1:
        n = (length + 1) // 2
        return sma(sma(close, n), n)
    return sma(sma(close, length // 2 + 1), length // 2)


@INDICATORS.register
class TRIMA(Indicator):
    """Triangular Moving Average.

    What: a smoother, middle-weighted MA (a double SMA).
    Best settings: ``length`` 20; longer for heavier smoothing.
    Edge cases: warm-up ~ length; odd/even length use different two-stage windows.
    Parity: TA-Lib ``TRIMA`` / pandas-ta ``trima``.
    """

    spec = IndicatorSpec(
        name="trima",
        category="trend",
        aliases=("Triangular MA",),
        inputs=(CLOSE,),
        outputs=("trima",),
        talib_compatible=True,
        references=("TA-Lib TRIMA", "pandas-ta trima", "tulip trima"),
        doc="ref/ta_docs/trend/misc_MA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return trima(df[CLOSE], self.params["length"])
