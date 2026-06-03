"""MACD — Moving Average Convergence Divergence (trend/momentum, Gerald Appel).

``MACD = EMA(fast) - EMA(slow)``; ``Signal = EMA(MACD, signal)``; ``Hist = MACD - Signal``.
Composes ``base.ema`` (so the EMA seeding convention flows through all three outputs).
See ``ref/ta_docs/trend/MACD.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def macd(
    close: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    talib_compatible: bool = True,
) -> dict:
    """Return the MACD line, signal line, and histogram."""
    macd_line = ema(close, fast, talib_compatible) - ema(close, slow, talib_compatible)
    signal_line = ema(macd_line, signal, talib_compatible)
    return {
        "macd": macd_line,
        "macd_signal": signal_line,
        "macd_hist": macd_line - signal_line,
    }


@INDICATORS.register
class MACD(Indicator):
    """Moving Average Convergence Divergence.

    What: fast-minus-slow EMA (the MACD line), its EMA (signal), and their difference (hist).
    Best settings: 12/26/9 (classic); 5/35/5 faster. MACD crossing signal = momentum shift.
    Edge cases: meaningful only after ~slow+signal bars; EMA seeding flows to all outputs.
    Parity: TA-Lib ``MACD`` / pandas-ta ``macd`` (SMA-seeded EMAs).
    """

    spec = IndicatorSpec(
        name="macd",
        category="trend",
        aliases=("Moving Average Convergence Divergence",),
        inputs=(CLOSE,),
        outputs=("macd", "macd_signal", "macd_hist"),
        talib_compatible=True,
        references=("Appel", "TA-Lib MACD", "pandas-ta macd"),
        doc="ref/ta_docs/trend/MACD.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        fast: int = Field(default=12, ge=1)
        slow: int = Field(default=26, ge=1)
        signal: int = Field(default=9, ge=1)
        talib_compatible: bool = True

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return macd(df[CLOSE], p["fast"], p["slow"], p["signal"], p["talib_compatible"])
