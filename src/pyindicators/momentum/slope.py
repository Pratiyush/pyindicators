"""Slope — per-bar rate of change of price (``close.diff(length) / length``)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def slope(close: pd.Series, length: int = 1) -> pd.Series:
    """Slope = (close - close_{t-length}) / length."""
    return close.diff(length) / length


@INDICATORS.register
class Slope(Indicator):
    """Slope.

    What: the average per-bar price change over ``length`` bars (rise/run).
    Best settings: ``length`` 1.
    Edge cases: first ``length`` bars NaN.
    Parity: pandas-ta ``slope``.
    """

    spec = IndicatorSpec(
        name="slope",
        category="momentum",
        aliases=("Slope",),
        inputs=(CLOSE,),
        outputs=("slope",),
        references=("pandas-ta slope",),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=1, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return slope(df[CLOSE], self.params["length"])
