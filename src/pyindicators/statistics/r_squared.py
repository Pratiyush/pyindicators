"""R-Squared — coefficient of determination of price vs a time ramp (statistics).

The square of the Pearson correlation between ``close`` and a straight time line over the
window: r^2 in [0, 1] = the fraction of price variance explained by a linear trend (0 = no
linear fit, 1 = a perfectly straight line). It is exactly ``cti`` (= ``linreg(..., r=True)``)
squared. Reuses the rolling-Pearson approach of ``momentum/cti.py`` and guards the division
with ``safe_divide``. See ``ref/ta_docs/statistics/misc_statistics.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide


def r_squared(close: pd.Series, length: int = 14) -> pd.Series:
    """Rolling coefficient of determination of ``close`` vs a time ramp over ``length`` (0..1).

    Squares the Pearson r of each window against ``arange(length)`` (the cti/linreg-r approach).
    A flat window has zero price variance -> r undefined -> NaN (guarded, not fabricated).
    """
    xd = np.arange(length, dtype="float64")
    xd -= xd.mean()
    sxx = float((xd * xd).sum())  # > 0 for length >= 2 (constant time variance)

    def _cov(w: np.ndarray) -> float:
        return float((xd * (w - w.mean())).sum())

    cov = close.rolling(length, min_periods=length).apply(_cov, raw=True)
    syy = close.rolling(length, min_periods=length).var(ddof=0) * length  # sum of squared dev
    # r^2 = cov^2 / (sxx * syy); safe_divide -> NaN where syy == 0 (flat window).
    return safe_divide(cov * cov, sxx * syy)


@INDICATORS.register
class RSquared(Indicator):
    """R-Squared (coefficient of determination).

    What: fraction of price variance explained by a straight-line fit over N bars (r^2, 0..1).
    Best settings: ``length`` 14; near 1 = clean trend, near 0 = no linear structure (chop).
    Edge cases: flat window (zero price variance) -> undefined -> NaN; first ``length-1`` NaN.
    Parity: closed-form (Pearson r of close vs arange, squared) == pandas-ta ``cti`` squared.
    """

    spec = IndicatorSpec(
        name="r_squared",
        category="statistics",
        aliases=("R-Squared", "Coefficient of Determination", "R2"),
        inputs=(CLOSE,),
        outputs=("r_squared",),
        bounds={"r_squared": (0.0, 1.0)},
        references=("coefficient of determination", "pandas-ta cti squared"),
        doc="ref/ta_docs/statistics/misc_statistics.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=2)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return r_squared(df[CLOSE], self.params["length"])
