"""SMA Slope — the per-bar slope of a simple moving average (trend direction check)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def sma_slope(close: pd.Series, length: int = 50) -> pd.Series:
    """Per-bar change of SMA(close, length): > 0 = rising MA, < 0 = falling MA."""
    return sma(close, length).diff()


@INDICATORS.register
class SMASlope(Indicator):
    """SMA Slope.

    What: the one-bar change of a moving average — a numeric "is the trend up?" check.
    Best settings: ``length`` 50 (or 150/200 for Minervini's MA-trending-up rule).
    Edge cases: first ``length`` bars NaN (SMA warm-up + one diff).
    Parity: derived from SMA (no external library needed).
    """

    spec = IndicatorSpec(
        name="sma_slope",
        category="trend",
        aliases=("SMA Slope",),
        inputs=(CLOSE,),
        outputs=("sma_slope",),
        references=("Minervini trend template",),
        doc="ref/ta_docs/base/SMA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=50, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return sma_slope(df[CLOSE], self.params["length"])
