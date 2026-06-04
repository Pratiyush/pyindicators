"""midprice — ``(max(high, N) + min(low, N)) / 2`` (price transform / overlap)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def midprice(df: pd.DataFrame, length: int = 14) -> pd.Series:
    """Midpoint of the highest high / lowest low over ``length`` bars."""
    hh = df[HIGH].rolling(length, min_periods=length).max()
    ll = df[LOW].rolling(length, min_periods=length).min()
    return (hh + ll) / 2.0


@INDICATORS.register
class Midprice(Indicator):
    """Midprice.

    What: midpoint of the highest high and lowest low over ``length`` bars.
    Best settings: ``length`` 14.
    Edge cases: first ``length-1`` bars NaN.
    Parity: TA-Lib ``MIDPRICE`` / pandas-ta ``midprice``.
    """

    spec = IndicatorSpec(
        name="midprice",
        category="price_transform",
        aliases=("MIDPRICE",),
        inputs=(HIGH, LOW),
        outputs=("midprice",),
        talib_compatible=True,
        references=("TA-Lib MIDPRICE", "pandas-ta midprice"),
        doc="ref/ta_docs/price_transform/price_transforms.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return midprice(df, self.params["length"])
