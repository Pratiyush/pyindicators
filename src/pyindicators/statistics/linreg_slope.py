"""LINEARREG_SLOPE — the slope of the rolling linear-regression line."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from ._ols import rolling_ols


def linreg_slope(close: pd.Series, length: int = 14) -> pd.Series:
    """Slope of the rolling linear-regression line over ``length`` bars."""
    return rolling_ols(close, length)[0]


@INDICATORS.register
class LinearRegSlope(Indicator):
    """Linear Regression Slope.

    What: the per-bar slope of the least-squares line — trend direction and steepness.
    Best settings: ``length`` 14; > 0 rising, < 0 falling.
    Edge cases: needs ``length`` >= 2.
    Parity: TA-Lib ``LINEARREG_SLOPE`` / pandas-ta ``slope``.
    """

    spec = IndicatorSpec(
        name="linreg_slope",
        category="statistics",
        aliases=("Linear Regression Slope",),
        inputs=(CLOSE,),
        outputs=("linreg_slope",),
        talib_compatible=True,
        references=("TA-Lib LINEARREG_SLOPE", "pandas-ta slope"),
        doc="ref/ta_docs/statistics/LinearRegression.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=2)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return linreg_slope(df[CLOSE], self.params["length"])
