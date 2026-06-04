"""LINEARREG — the value of a rolling linear-regression line at the current bar."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from ._ols import rolling_ols


def linreg(close: pd.Series, length: int = 14) -> pd.Series:
    """Linear-regression value at the current bar (endpoint of the fitted line)."""
    slope, intercept = rolling_ols(close, length)
    return intercept + slope * (length - 1)


@INDICATORS.register
class LinearReg(Indicator):
    """Linear Regression.

    What: the value of the least-squares line (fit over N bars) at the current bar.
    Best settings: ``length`` 14.
    Edge cases: needs ``length`` >= 2; first ``length-1`` bars NaN.
    Parity: TA-Lib ``LINEARREG`` / pandas-ta ``linreg``.
    """

    spec = IndicatorSpec(
        name="linreg",
        category="statistics",
        aliases=("Linear Regression", "LSMA"),
        inputs=(CLOSE,),
        outputs=("linreg",),
        talib_compatible=True,
        references=("TA-Lib LINEARREG", "pandas-ta linreg"),
        doc="ref/ta_docs/statistics/LinearRegression.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=2)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return linreg(df[CLOSE], self.params["length"])
