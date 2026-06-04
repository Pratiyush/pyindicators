"""Rolling Median — a robust central-tendency line (statistics)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def median(close: pd.Series, length: int = 30) -> pd.Series:
    """Rolling median of ``close`` over ``length`` bars."""
    return close.rolling(length, min_periods=length).median()


@INDICATORS.register
class Median(Indicator):
    """Rolling Median.

    What: the middle value over ``length`` bars — an outlier-robust smoother.
    Best settings: ``length`` 30.
    Edge cases: first ``length-1`` bars NaN.
    Parity: pandas-ta ``median``.
    """

    spec = IndicatorSpec(
        name="median",
        category="statistics",
        aliases=("Rolling Median",),
        inputs=(CLOSE,),
        outputs=("median",),
        references=("pandas-ta median",),
        doc="ref/ta_docs/statistics/misc_statistics.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=30, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return median(df[CLOSE], self.params["length"])
