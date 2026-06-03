"""PPO — Percentage Price Oscillator (trend/momentum).

MACD expressed in percent of the slow EMA, so it is comparable across price levels:
``PPO = 100 * (EMA(fast) - EMA(slow)) / EMA(slow)``; signal = EMA(PPO); hist = PPO - signal.
Composes ``base.ema``. See ``ref/ta_docs/trend/PPO.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide


def ppo(
    close: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    talib_compatible: bool = True,
) -> dict:
    """Percentage Price Oscillator line, signal, and histogram."""
    ef = ema(close, fast, talib_compatible)
    es = ema(close, slow, talib_compatible)
    line = 100.0 * safe_divide(ef - es, es)
    signal_line = ema(line, signal, talib_compatible)
    return {"ppo": line, "ppo_signal": signal_line, "ppo_hist": line - signal_line}


@INDICATORS.register
class PPO(Indicator):
    """Percentage Price Oscillator.

    What: MACD in percentage terms (normalised by the slow EMA) for cross-asset comparison.
    Best settings: 12/26/9 (classic). APO is the same but absolute (non-normalised).
    Edge cases: slow EMA 0 -> guarded (degenerate data only).
    Parity: pandas-ta ``ppo`` (clean SMA-seeded EMAs; TA-Lib restarts the fast EMA).
    """

    spec = IndicatorSpec(
        name="ppo",
        category="trend",
        aliases=("Percentage Price Oscillator",),
        inputs=(CLOSE,),
        outputs=("ppo", "ppo_signal", "ppo_hist"),
        talib_compatible=True,
        references=("TA-Lib PPO", "pandas-ta ppo"),
        doc="ref/ta_docs/trend/PPO.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        fast: int = Field(default=12, ge=1)
        slow: int = Field(default=26, ge=1)
        signal: int = Field(default=9, ge=1)
        talib_compatible: bool = True

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return ppo(df[CLOSE], p["fast"], p["slow"], p["signal"], p["talib_compatible"])
