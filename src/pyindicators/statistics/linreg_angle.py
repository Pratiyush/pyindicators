"""LINEARREG_ANGLE — the angle (degrees) of the rolling linear-regression line."""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from ._ols import rolling_ols


def linreg_angle(close: pd.Series, length: int = 14) -> pd.Series:
    """Angle in degrees of the rolling linear-regression slope."""
    slope = rolling_ols(close, length)[0]
    return np.degrees(np.arctan(slope))


@INDICATORS.register
class LinearRegAngle(Indicator):
    """Linear Regression Angle.

    What: the regression slope expressed as an angle in degrees (-90..90).
    Best settings: ``length`` 14.
    Edge cases: needs ``length`` >= 2.
    Parity: TA-Lib ``LINEARREG_ANGLE``.
    """

    spec = IndicatorSpec(
        name="linreg_angle",
        category="statistics",
        aliases=("Linear Regression Angle",),
        inputs=(CLOSE,),
        outputs=("linreg_angle",),
        bounds={"linreg_angle": (-90.0, 90.0)},
        talib_compatible=True,
        references=("TA-Lib LINEARREG_ANGLE",),
        doc="ref/ta_docs/statistics/LinearRegression.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=2)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return linreg_angle(df[CLOSE], self.params["length"])
