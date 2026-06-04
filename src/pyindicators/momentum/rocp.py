"""ROCP — Rate of Change Percentage: ``(close - close_{t-n}) / close_{t-n}`` (fraction)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide


def rocp(close: pd.Series, length: int = 10) -> pd.Series:
    """Rate of change as a fraction (not percent)."""
    prev = close.shift(length)
    return safe_divide(close - prev, prev)


@INDICATORS.register
class ROCP(Indicator):
    """Rate of Change Percentage (fraction).

    What: ROC expressed as a fraction (ROC/100).
    Best settings: ``length`` 10.
    Edge cases: zero base -> guarded to NaN.
    Parity: TA-Lib ``ROCP`` / pandas-ta ``roc`` (scaled).
    """

    spec = IndicatorSpec(
        name="rocp",
        category="momentum",
        aliases=("Rate of Change Percentage",),
        inputs=(CLOSE,),
        outputs=("rocp",),
        talib_compatible=True,
        references=("TA-Lib ROCP",),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=10, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return rocp(df[CLOSE], self.params["length"])
