"""APO — Absolute Price Oscillator (trend/momentum).

The MACD line without a signal: ``APO = EMA(fast) - EMA(slow)`` (absolute, not normalised
like PPO). Composes ``base.ema``. See ``ref/ta_docs/trend/PPO.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def apo(close: pd.Series, fast: int = 12, slow: int = 26, talib_compatible: bool = True) -> pd.Series:
    """Absolute Price Oscillator = EMA(fast) - EMA(slow)."""
    return ema(close, fast, talib_compatible) - ema(close, slow, talib_compatible)


@INDICATORS.register
class APO(Indicator):
    """Absolute Price Oscillator.

    What: the difference of a fast and slow EMA (the MACD line, no signal).
    Best settings: 12/26. PPO is the percentage-normalised version.
    Edge cases: inherits EMA seeding/warm-up.
    Parity: pandas-ta ``apo`` (clean SMA-seeded EMAs; TA-Lib restarts the fast EMA).
    """

    spec = IndicatorSpec(
        name="apo",
        category="trend",
        aliases=("Absolute Price Oscillator",),
        inputs=(CLOSE,),
        outputs=("apo",),
        talib_compatible=True,
        references=("TA-Lib APO", "pandas-ta apo"),
        doc="ref/ta_docs/trend/PPO.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        fast: int = Field(default=12, ge=1)
        slow: int = Field(default=26, ge=1)
        talib_compatible: bool = True

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        p = self.params
        return apo(df[CLOSE], p["fast"], p["slow"], p["talib_compatible"])
