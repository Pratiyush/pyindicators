"""BETA — rolling regression slope of one return series on another (TA-Lib ``BETA``).

What: the ordinary-least-squares slope of ``real1``'s one-period percentage returns regressed
on ``real0``'s returns over ``length`` bars. With the canonical ``BETA(high, low)`` wiring this
is the slope of *low* returns (y) on *high* returns (x) — a sensitivity/co-movement statistic.
Closed form per window: ``beta = (n*Sxy - Sx*Sy) / (n*Sxx - Sx*Sx)`` with ``x`` = high returns,
``y`` = low returns and ``n = length``. Composes the rolling-sum primitive and ``safe_divide``
(no re-inlined base math). See ``ref/ta_docs/statistics/misc_statistics.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec, safe_divide


def beta(high: pd.Series, low: pd.Series, length: int = 5) -> pd.Series:
    """Rolling TA-Lib beta: slope of ``low`` returns on ``high`` returns over ``length`` bars.

    Inputs are converted to one-period percentage returns first (``pct_change``); the slope is
    then the least-squares regression of the ``low`` returns (regressand) on the ``high`` returns
    (regressor), matching ``talib.BETA(real0=high, real1=low)`` exactly.

    Edge handling falls out of the closed form: a window with zero return-variance on ``high``
    (e.g. a flat high) makes the denominator 0; TA-Lib emits ``0.0`` there, so we fill 0.0 (the
    warm-up rows stay NaN because their denominator is NaN, not exactly 0).
    """
    n = length
    x = high.pct_change()  # real0 returns -> regressor
    y = low.pct_change()  # real1 returns -> regressand
    sum_x = x.rolling(n, min_periods=n).sum()
    sum_y = y.rolling(n, min_periods=n).sum()
    sum_xx = (x * x).rolling(n, min_periods=n).sum()
    sum_xy = (x * y).rolling(n, min_periods=n).sum()
    num = n * sum_xy - sum_x * sum_y
    den = n * sum_xx - sum_x * sum_x
    return safe_divide(num, den, fill=0.0)  # TA-Lib outputs 0.0 when Var(high returns) == 0


@INDICATORS.register
class Beta(Indicator):
    """Beta.

    What: rolling OLS slope of ``low`` percentage returns on ``high`` percentage returns.
    Best settings: ``length`` 5 (TA-Lib default); a longer window for a steadier estimate.
    Edge cases: flat-``high`` window (zero return variance) -> denominator 0 -> 0.0 (TA-Lib
    convention); warm-up (< ``length`` returns) -> NaN.
    Parity: TA-Lib ``BETA`` (real0=high, real1=low; pct-return regression slope; 0.0 on zero
    variance). NOT pandas-ta ``beta`` (that is the CAPM Cov/Var on close vs a benchmark).
    """

    spec = IndicatorSpec(
        name="beta",
        category="statistics",
        aliases=("Beta",),
        inputs=(HIGH, LOW),
        outputs=("beta",),
        talib_compatible=True,
        references=("TA-Lib BETA",),
        doc="ref/ta_docs/statistics/misc_statistics.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=5, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return beta(df[HIGH], df[LOW], self.params["length"])
