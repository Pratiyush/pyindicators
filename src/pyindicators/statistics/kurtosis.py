"""Rolling Kurtosis — tailedness of the distribution over a window (statistics)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def kurtosis(close: pd.Series, length: int = 30) -> pd.Series:
    """Rolling (excess) kurtosis of ``close`` over ``length`` bars."""
    return close.rolling(length, min_periods=length).kurt()


@INDICATORS.register
class Kurtosis(Indicator):
    """Rolling Kurtosis.

    What: excess kurtosis over ``length`` bars (>0 fat-tailed vs normal).
    Best settings: ``length`` 30.
    Edge cases: needs >= 4 points; first ``length-1`` bars NaN.
    Parity: pandas-ta ``kurtosis``.
    """

    spec = IndicatorSpec(
        name="kurtosis",
        category="statistics",
        aliases=("Rolling Kurtosis",),
        inputs=(CLOSE,),
        outputs=("kurtosis",),
        references=("pandas-ta kurtosis",),
        doc="ref/ta_docs/statistics/misc_statistics.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=30, ge=4)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return kurtosis(df[CLOSE], self.params["length"])
