"""TSF — Time Series Forecast: the regression line projected one bar ahead."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from ._ols import rolling_ols


def tsf(close: pd.Series, length: int = 14) -> pd.Series:
    """Time Series Forecast = regression value projected to the next bar (x = length)."""
    slope, intercept = rolling_ols(close, length)
    return intercept + slope * length


@INDICATORS.register
class TSF(Indicator):
    """Time Series Forecast.

    What: the linear-regression line extended one bar into the future (LINEARREG + slope).
    Best settings: ``length`` 14.
    Edge cases: needs ``length`` >= 2.
    Parity: TA-Lib ``TSF`` / pandas-ta ``tsf``.
    """

    spec = IndicatorSpec(
        name="tsf",
        category="statistics",
        aliases=("Time Series Forecast",),
        inputs=(CLOSE,),
        outputs=("tsf",),
        talib_compatible=True,
        references=("TA-Lib TSF", "pandas-ta tsf"),
        doc="ref/ta_docs/statistics/LinearRegression.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=2)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return tsf(df[CLOSE], self.params["length"])
