"""Mean Absolute Deviation (MAD) — average absolute distance from the rolling mean."""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def mad(close: pd.Series, length: int = 30) -> pd.Series:
    """Rolling mean absolute deviation over ``length`` bars."""
    return close.rolling(length, min_periods=length).apply(
        lambda w: np.abs(w - w.mean()).mean(), raw=True
    )


@INDICATORS.register
class MAD(Indicator):
    """Mean Absolute Deviation.

    What: average absolute deviation from the window mean — a robust dispersion measure.
    Best settings: ``length`` 30.
    Edge cases: constant window -> 0; first ``length-1`` bars NaN.
    Parity: pandas-ta ``mad``.
    """

    spec = IndicatorSpec(
        name="mad",
        category="statistics",
        aliases=("Mean Absolute Deviation",),
        inputs=(CLOSE,),
        outputs=("mad",),
        references=("pandas-ta mad",),
        doc="ref/ta_docs/statistics/misc_statistics.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=30, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return mad(df[CLOSE], self.params["length"])
