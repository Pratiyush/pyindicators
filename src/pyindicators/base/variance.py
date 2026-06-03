"""Rolling Variance (base / statistics primitive).

The square of the rolling standard deviation; base for several statistics functions.
Population (``ddof=0``) by default to match TA-Lib ``VAR``. See ``ref/ta_docs/base/RollingStdev.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def variance(series: pd.Series, length: int, ddof: int = 0) -> pd.Series:
    """Rolling variance (``ddof=0`` population by default, matching TA-Lib ``VAR``)."""
    return series.rolling(length, min_periods=length).var(ddof=ddof)


@INDICATORS.register
class Variance(Indicator):
    """Rolling Variance.

    What: mean squared deviation from the rolling mean over ``length`` bars (non-negative).
    Best settings: ``length`` 20; ``ddof`` 0 = population (TA-Lib), 1 = sample.
    Edge cases: constant series -> 0; N=1 population = 0, sample undefined (NaN).
    Parity: TA-Lib ``VAR`` (``ddof=0``); pandas-ta ``variance``.
    """

    spec = IndicatorSpec(
        name="variance",
        category="base",
        aliases=("VAR", "Moving Variance"),
        inputs=(CLOSE,),
        outputs=("variance",),
        talib_compatible=True,
        references=("TA-Lib VAR", "pandas-ta variance", "tulip var"),
        doc="ref/ta_docs/base/RollingStdev.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=1)
        ddof: int = Field(default=0, ge=0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return variance(df[CLOSE], self.params["length"], self.params["ddof"])
