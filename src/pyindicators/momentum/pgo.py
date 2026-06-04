"""PGO — Pretty Good Oscillator (Mark Johnson): distance from SMA in ATR units."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema, sma
from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec, safe_divide
from pyindicators.volatility.atr import atr


def pgo(df: pd.DataFrame, length: int = 14) -> pd.Series:
    """Pretty Good Oscillator = (close - SMA(close, N)) / EMA(ATR(N), N)."""
    return safe_divide(df[CLOSE] - sma(df[CLOSE], length), ema(atr(df, length), length))


@INDICATORS.register
class PGO(Indicator):
    """Pretty Good Oscillator.

    What: how far price is from its SMA, measured in average-true-range units.
    Best settings: ``length`` 14; > 3 / < -3 are notable extremes.
    Edge cases: zero EMA(TR) (flat) guarded; inherits warm-up.
    Parity: pandas-ta ``pgo``.
    """

    spec = IndicatorSpec(
        name="pgo",
        category="momentum",
        aliases=("Pretty Good Oscillator",),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("pgo",),
        references=("Mark Johnson", "pandas-ta pgo"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return pgo(df, self.params["length"])
