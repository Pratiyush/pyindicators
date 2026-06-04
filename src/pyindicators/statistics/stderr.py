"""STDERR — standard error of the rolling linear-regression fit (statistics).

The standard error *of the regression* (a.k.a. residual standard error): how far price
typically sits from the least-squares trend line fitted over each trailing window. For each
window it fits ``y = intercept + slope * x`` (x = 0..length-1, via the shared OLS helper used
by ``linreg``/``tsf``), forms the fitted line, takes the residuals ``close - fitted``, and
reports ``sqrt( sum(residual^2) / (length - 2) )`` — residual std with ``ddof=2`` (two
estimated parameters: slope and intercept). Small = price hugs the trend; large = noisy fit.

Distinct from pandas-ta ``stderr`` (which is ``stdev(close)/sqrt(length)`` — the standard
error *of the mean*, a different quantity). Composes ``statistics._ols.rolling_ols`` for the
slope/intercept and guards the ``/(length-2)`` normalisation with ``safe_divide``.
See ``ref/ta_docs/statistics/misc_statistics.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide

from ._ols import rolling_ols


def stderr(close: pd.Series, length: int = 14) -> pd.Series:
    """Standard error of the rolling OLS fit of ``close`` over ``length`` bars (ddof=2).

    Composes the shared rolling OLS to get the line's slope (Syy and the OLS identity
    ``SSR = Syy - slope^2 * Sxx`` give the residual sum of squares without re-fitting), then
    normalises by ``length - 2``. The first ``length - 1`` bars are NaN (warm-up); a perfectly
    straight window has zero residuals -> 0 (an exact fit, not undefined).
    """
    slope, _ = rolling_ols(close, length)
    x = np.arange(length, dtype="float64")
    sxx = float(((x - x.mean()) ** 2).sum())  # time variance of the ramp; > 0 for length >= 2
    syy = close.rolling(length, min_periods=length).var(ddof=0) * length  # sum of sq deviations
    # OLS decomposition: total SS = explained (slope^2 * Sxx) + residual SS. Clip the tiny
    # negative that floating-point cancellation can produce on a near-perfect fit.
    ssr = (syy - slope * slope * sxx).clip(lower=0.0)
    return np.sqrt(safe_divide(ssr, pd.Series(float(length - 2), index=close.index)))


@INDICATORS.register
class StdErr(Indicator):
    """Standard Error (of the linear-regression fit).

    What: residual standard error of the least-squares trend line over N bars
        (``sqrt(SSR / (N-2))``) — typical distance of price from its own regression line.
    Best settings: ``length`` 14; pairs with ``linreg``/``tsf`` as a fit-quality band width.
    Edge cases: needs ``length`` >= 3 (two params consume two dof); a perfectly straight
        window -> 0; first ``length-1`` bars NaN.
    Parity: closed-form OLS residual std == ``stdev(close, ddof=1) * sqrt((1-r^2)(N-1)/(N-2))``
        (cross-checked vs pandas-ta ``stdev``). NOT pandas-ta ``stderr`` (std of the mean).
    """

    spec = IndicatorSpec(
        name="stderr",
        category="statistics",
        aliases=("Standard Error", "Regression Standard Error", "STDERR"),
        inputs=(CLOSE,),
        outputs=("stderr",),
        references=("standard error of regression", "pandas-ta stdev identity"),
        doc="ref/ta_docs/statistics/misc_statistics.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=3)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return stderr(df[CLOSE], self.params["length"])
