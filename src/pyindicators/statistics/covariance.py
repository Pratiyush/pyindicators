"""Covariance — rolling sample covariance of high and low (statistics).

Measures how the high and low of each bar co-move over a trailing window: positive when
they tend to rise/fall together (typical for trending bars), near zero when their daily
extremes move independently. Scale-dependent (units are price-squared), so it grows with
price level and with bar range. A pure trailing rolling statistic with no smoothing.

``cov_t = sum_{i in window}(h_i - mean_h)(l_i - mean_l) / (N - ddof)`` over the last
``length`` bars, i.e. the sample covariance (``ddof=1``) of ``high`` against ``low``. This
is exactly pandas' ``high.rolling(length).cov(low)``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def covariance(high: pd.Series, low: pd.Series, length: int = 30, ddof: int = 1) -> pd.Series:
    """Rolling sample covariance of ``high`` and ``low`` over ``length`` bars.

    Divisor is ``N - ddof`` (``ddof=1`` -> sample covariance, matching pandas). The first
    ``length - 1`` bars are NaN (warm-up); a window with fewer than ``ddof + 1`` finite
    points is NaN as well. A flat window (zero variance in either series) yields 0.0, which
    is correct: there is no co-movement to measure.
    """
    return high.rolling(length, min_periods=length).cov(low, ddof=ddof)


@INDICATORS.register
class Covariance(Indicator):
    """Rolling Covariance (high vs low).

    What: trailing sample covariance of the bar high against the bar low over ``length``.
    Best settings: ``length`` 30; positive => H/L co-move (trend), ~0 => independent extremes.
    Edge cases: first ``length-1`` bars NaN; needs >= ``ddof+1`` points; flat window -> 0.0.
    Parity: pandas ``high.rolling(length).cov(low)`` (sample covariance, ``ddof=1``) — the
        canonical oracle; no TA library exposes a direct rolling-covariance equivalent.
    """

    spec = IndicatorSpec(
        name="covariance",
        category="statistics",
        aliases=("Rolling Covariance", "COV"),
        inputs=(HIGH, LOW),
        outputs=("covariance",),
        references=("pandas Series.rolling.cov",),
        doc="ref/ta_docs/statistics/misc_statistics.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=30, ge=2)
        ddof: int = Field(default=1, ge=0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return covariance(df[HIGH], df[LOW], self.params["length"], self.params["ddof"])
