"""Percent From High — how far below the N-bar high the close sits (<= 0)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, HIGH, INDICATORS, Indicator, IndicatorSpec, safe_divide


def pct_from_high(df: pd.DataFrame, length: int = 252) -> pd.Series:
    """Percent distance of close below the ``length``-bar high: 100*(close - HH)/HH."""
    hh = df[HIGH].rolling(length, min_periods=length).max()
    return 100.0 * safe_divide(df[CLOSE] - hh, hh)


@INDICATORS.register
class PctFromHigh(Indicator):
    """Percent From High.

    What: how far (in %) the close is below its N-bar high; 0 = at a new high (<= 0 otherwise).
    Best settings: ``length`` 252; Minervini wants price within 25% of the 52-week high.
    Edge cases: first ``length-1`` bars NaN.
    Parity: trailing-max based (no external library needed).
    """

    spec = IndicatorSpec(
        name="pct_from_high",
        category="structure",
        aliases=("Percent From High",),
        inputs=(HIGH, CLOSE),
        outputs=("pct_from_high",),
        references=("Minervini trend template",),
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=252, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return pct_from_high(df, self.params["length"])
