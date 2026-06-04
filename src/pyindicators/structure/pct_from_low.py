"""Percent From Low — how far above the N-bar low the close sits (>= 0)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, LOW, Indicator, IndicatorSpec, safe_divide


def pct_from_low(df: pd.DataFrame, length: int = 252) -> pd.Series:
    """Percent distance of close above the ``length``-bar low: 100*(close - LL)/LL."""
    ll = df[LOW].rolling(length, min_periods=length).min()
    return 100.0 * safe_divide(df[CLOSE] - ll, ll)


@INDICATORS.register
class PctFromLow(Indicator):
    """Percent From Low.

    What: how far (in %) the close is above its N-bar low; >= 0 (0 = at a new low).
    Best settings: ``length`` 252; Minervini wants price >= 30% above the 52-week low.
    Edge cases: first ``length-1`` bars NaN.
    Parity: trailing-min based (no external library needed).
    """

    spec = IndicatorSpec(
        name="pct_from_low",
        category="structure",
        aliases=("Percent From Low",),
        inputs=(LOW, CLOSE),
        outputs=("pct_from_low",),
        references=("Minervini trend template",),
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=252, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return pct_from_low(df, self.params["length"])
