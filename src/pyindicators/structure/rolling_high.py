"""Rolling High — the highest high over N bars (e.g. the 52-week high)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import HIGH, INDICATORS, Indicator, IndicatorSpec


def rolling_high(df: pd.DataFrame, length: int = 252) -> pd.Series:
    """Highest high over a trailing window of ``length`` bars."""
    return df[HIGH].rolling(length, min_periods=length).max()


@INDICATORS.register
class RollingHigh(Indicator):
    """Rolling High.

    What: the highest high over the last ``length`` bars (252 ~ the 52-week high on dailies).
    Best settings: ``length`` 252 (52-week); 20/50 for shorter structure.
    Edge cases: first ``length-1`` bars NaN.
    Parity: trailing-max (no external library needed).
    """

    spec = IndicatorSpec(
        name="rolling_high",
        category="structure",
        aliases=("Highest High", "52-week High"),
        inputs=(HIGH,),
        outputs=("rolling_high",),
        references=("Minervini trend template",),
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=252, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return rolling_high(df, self.params["length"])
