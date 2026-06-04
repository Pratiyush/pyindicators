"""midpoint — ``(max(close, N) + min(close, N)) / 2`` (price transform / overlap)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def midpoint(close: pd.Series, length: int = 14) -> pd.Series:
    """Midpoint of the highest/lowest close over ``length`` bars."""
    hh = close.rolling(length, min_periods=length).max()
    ll = close.rolling(length, min_periods=length).min()
    return (hh + ll) / 2.0


@INDICATORS.register
class Midpoint(Indicator):
    """Midpoint.

    What: midpoint of the highest and lowest close over ``length`` bars.
    Best settings: ``length`` 14.
    Edge cases: first ``length-1`` bars NaN.
    Parity: TA-Lib ``MIDPOINT`` / pandas-ta ``midpoint``.
    """

    spec = IndicatorSpec(
        name="midpoint",
        category="price_transform",
        aliases=("MIDPOINT",),
        inputs=(CLOSE,),
        outputs=("midpoint",),
        talib_compatible=True,
        references=("TA-Lib MIDPOINT", "pandas-ta midpoint"),
        doc="ref/ta_docs/price_transform/price_transforms.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return midpoint(df[CLOSE], self.params["length"])
