"""TTM Trend (John Carter) — +1/-1 based on close vs the average of recent hl2.

``trend_avg = mean(hl2_t, hl2_{t-1}, ..., hl2_{t-length})``; +1 if close > trend_avg else -1.
See ``ref/ta_docs/trend/README.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def ttm_trend(df: pd.DataFrame, length: int = 6) -> pd.Series:
    """TTM Trend: +1 when close is above the mean of the last ``length`` hl2 values, else -1."""
    hl2 = (df[HIGH] + df[LOW]) / 2.0
    trend_avg = hl2.copy()
    for i in range(1, length):
        trend_avg = trend_avg + hl2.shift(i)
    trend_avg = trend_avg / length
    result = pd.Series(np.where(df[CLOSE] > trend_avg, 1.0, -1.0), index=df.index)
    return result.where(trend_avg.notna())  # NaN during warm-up


@INDICATORS.register
class TTMTrend(Indicator):
    """TTM Trend.

    What: a +1/-1 trend flag from close versus the average of recent median prices.
    Best settings: ``length`` 6 (Carter); used to colour bars.
    Edge cases: first ``length`` bars NaN (warm-up).
    Parity: pandas-ta ``ttm_trend``.
    """

    spec = IndicatorSpec(
        name="ttm_trend",
        category="trend",
        aliases=("TTM Trend",),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("ttm_trend",),
        bounds={"ttm_trend": (-1.0, 1.0)},
        references=("Carter", "pandas-ta ttm_trend"),
        doc="ref/ta_docs/trend/README.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=6, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return ttm_trend(df, self.params["length"])
