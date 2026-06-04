"""Rolling Low — the lowest low over N bars (e.g. the 52-week low)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import INDICATORS, LOW, Indicator, IndicatorSpec


def rolling_low(df: pd.DataFrame, length: int = 252) -> pd.Series:
    """Lowest low over a trailing window of ``length`` bars."""
    return df[LOW].rolling(length, min_periods=length).min()


@INDICATORS.register
class RollingLow(Indicator):
    """Rolling Low.

    What: the lowest low over the last ``length`` bars (252 ~ the 52-week low on dailies).
    Best settings: ``length`` 252 (52-week); 20/50 for shorter structure.
    Edge cases: first ``length-1`` bars NaN.
    Parity: trailing-min (no external library needed).
    """

    spec = IndicatorSpec(
        name="rolling_low",
        category="structure",
        aliases=("Lowest Low", "52-week Low"),
        inputs=(LOW,),
        outputs=("rolling_low",),
        references=("Minervini trend template",),
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=252, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return rolling_low(df, self.params["length"])
