"""Z-Score — standardised distance of price from its rolling mean (statistics).

``z = (close - SMA(close, N)) / stdev(close, N)``. Uses sample stdev (ddof=1) to match
pandas-ta. See ``ref/ta_docs/statistics/misc_statistics.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide


def zscore(close: pd.Series, length: int = 30, ddof: int = 1) -> pd.Series:
    """Rolling z-score of ``close`` over ``length`` bars (guarded against zero stdev)."""
    mean = close.rolling(length, min_periods=length).mean()
    std = close.rolling(length, min_periods=length).std(ddof=ddof)
    return safe_divide(close - mean, std)


@INDICATORS.register
class ZScore(Indicator):
    """Z-Score.

    What: how many standard deviations price is from its rolling mean.
    Best settings: ``length`` 30; |z| > 2 = statistically extreme.
    Edge cases: stdev 0 (flat window) -> guarded to NaN.
    Parity: pandas-ta ``zscore`` (sample stdev).
    """

    spec = IndicatorSpec(
        name="zscore",
        category="statistics",
        aliases=("Z-Score",),
        inputs=(CLOSE,),
        outputs=("zscore",),
        references=("pandas-ta zscore",),
        doc="ref/ta_docs/statistics/misc_statistics.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=30, ge=2)
        ddof: int = Field(default=1, ge=0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return zscore(df[CLOSE], self.params["length"], self.params["ddof"])
