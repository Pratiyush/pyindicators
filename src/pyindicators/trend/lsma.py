"""LSMA — Least Squares Moving Average (a.k.a. Linear Regression Curve / End-Point MA).

The LSMA value at each bar is the endpoint of the least-squares line fitted over the trailing
``length`` bars — i.e. it is *exactly* the linear-regression value, so this simply composes
``statistics.linreg`` rather than re-deriving the normal equations. Versus an SMA it lags less
and "leads" in a steady trend (the fitted line's endpoint sits ahead of a centred average).
See ``ref/ta_docs/statistics/LinearRegression.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec
from pyindicators.statistics.linreg import linreg


def lsma(close: pd.Series, length: int = 14) -> pd.Series:
    """Least Squares MA over ``length`` bars: the rolling linear-regression endpoint value."""
    return linreg(close, length)


@INDICATORS.register
class LSMA(Indicator):
    """Least Squares Moving Average.

    What: the endpoint of the rolling least-squares line — identical to LINEARREG, used as an MA.
    Why: lower-lag trend follower; the regression endpoint leads a centred average in a trend.
    How: composes ``statistics.linreg`` (closed-form rolling OLS over ``x = 0..length-1``).
    Inputs: ``close``. Output: ``lsma`` (same scale as price). Causal (trailing window only).
    Best settings: ``length`` 14 (TA-Lib default); 25/50 for slower trend lines.
    Edge cases: needs ``length`` >= 2; first ``length-1`` bars NaN; a flat window -> flat line.
    Parity: TA-Lib ``LINEARREG`` / pandas-ta ``linreg`` (LSMA is the linear-regression value).
    """

    spec = IndicatorSpec(
        name="lsma",
        category="trend",
        aliases=("Least Squares Moving Average", "Linear Regression Curve", "End-Point MA"),
        inputs=(CLOSE,),
        outputs=("lsma",),
        talib_compatible=True,
        references=("TA-Lib LINEARREG", "pandas-ta linreg"),
        doc="ref/ta_docs/statistics/LinearRegression.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=2)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return lsma(df[CLOSE], self.params["length"])
