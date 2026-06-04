"""MA Spread — difference between a fast and a slow SMA (a regime feature; Aronson)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def ma_spread(close: pd.Series, fast: int = 50, slow: int = 200) -> pd.Series:
    """SMA(close, fast) - SMA(close, slow): > 0 = fast above slow (bullish regime)."""
    return sma(close, fast) - sma(close, slow)


@INDICATORS.register
class MASpread(Indicator):
    """MA Spread.

    What: the gap between a fast and slow SMA — one of Aronson's most-validated regime features.
    Best settings: 50 / 200; > 0 = golden-cross regime, < 0 = death-cross regime.
    Edge cases: warm-up = slow length.
    Parity: difference of two SMAs (validated against the explicit definition).
    """

    spec = IndicatorSpec(
        name="ma_spread",
        category="trend",
        aliases=("MA Spread", "MA Distance"),
        inputs=(CLOSE,),
        outputs=("ma_spread",),
        references=("Aronson, Evidence-Based TA",),
        doc="ref/ta_docs/trend/misc_MA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        fast: int = Field(default=50, ge=1)
        slow: int = Field(default=200, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return ma_spread(df[CLOSE], self.params["fast"], self.params["slow"])
