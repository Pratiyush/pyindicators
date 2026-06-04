"""LINEARREG_INTERCEPT — the intercept (value at the window start) of the regression line."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from ._ols import rolling_ols


def linreg_intercept(close: pd.Series, length: int = 14) -> pd.Series:
    """Intercept of the rolling linear-regression line (value at the window's first bar)."""
    return rolling_ols(close, length)[1]


@INDICATORS.register
class LinearRegIntercept(Indicator):
    """Linear Regression Intercept.

    What: the fitted line's value at the start of the N-bar window.
    Best settings: ``length`` 14.
    Edge cases: needs ``length`` >= 2.
    Parity: TA-Lib ``LINEARREG_INTERCEPT``.
    """

    spec = IndicatorSpec(
        name="linreg_intercept",
        category="statistics",
        aliases=("Linear Regression Intercept",),
        inputs=(CLOSE,),
        outputs=("linreg_intercept",),
        talib_compatible=True,
        references=("TA-Lib LINEARREG_INTERCEPT",),
        doc="ref/ta_docs/statistics/LinearRegression.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=2)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return linreg_intercept(df[CLOSE], self.params["length"])
