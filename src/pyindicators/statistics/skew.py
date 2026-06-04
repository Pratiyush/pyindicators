"""Rolling Skew — asymmetry of the return/price distribution over a window (statistics)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def skew(close: pd.Series, length: int = 30) -> pd.Series:
    """Rolling skewness of ``close`` over ``length`` bars."""
    return close.rolling(length, min_periods=length).skew()


@INDICATORS.register
class Skew(Indicator):
    """Rolling Skew.

    What: distribution asymmetry over ``length`` bars (>0 right-tailed, <0 left-tailed).
    Best settings: ``length`` 30.
    Edge cases: needs >= 3 points; first ``length-1`` bars NaN.
    Parity: pandas-ta ``skew``.
    """

    spec = IndicatorSpec(
        name="skew",
        category="statistics",
        aliases=("Rolling Skew",),
        inputs=(CLOSE,),
        outputs=("skew",),
        references=("pandas-ta skew",),
        doc="ref/ta_docs/statistics/misc_statistics.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=30, ge=3)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return skew(df[CLOSE], self.params["length"])
