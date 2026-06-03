"""RSI — Relative Strength Index (momentum oscillator, Wilder 1978).

Speed/magnitude of recent gains vs losses on a 0-100 scale. Uses Wilder's RMA (NOT a
2/(N+1) EMA — that would be "Cutler's RSI" and the classic "doesn't match TradingView" bug).
Composes ``base.rma``. See ``ref/ta_docs/momentum/RSI.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import rma
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def rsi(close: pd.Series, length: int = 14) -> pd.Series:
    """Wilder's RSI on ``close`` over ``length`` bars, bounded [0, 100].

    Edge handling falls out of the arithmetic: pure gains -> AvgLoss 0 -> RSI 100; pure
    losses -> RSI 0; a fully flat window -> 0/0 -> NaN (undefined, not fabricated).
    """
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    avg_gain = rma(gain, length)
    avg_loss = rma(loss, length)
    with np.errstate(divide="ignore", invalid="ignore"):
        rs = avg_gain / avg_loss
        return 100.0 - 100.0 / (1.0 + rs)


@INDICATORS.register
class RSI(Indicator):
    """Relative Strength Index.

    What: Wilder's bounded momentum oscillator (0-100) of smoothed gains vs losses.
    Best settings: 14 (Wilder); 2 for Connors mean-reversion; bands 70/30 (80/20 in trends).
    Edge cases: AvgLoss 0 -> 100; AvgGain 0 -> 0; flat series -> NaN.
    Parity: TA-Lib ``RSI`` / pandas-ta ``rsi`` (Wilder RMA, SMA-seeded first average).
    """

    spec = IndicatorSpec(
        name="rsi",
        category="momentum",
        aliases=("Relative Strength Index",),
        inputs=(CLOSE,),
        outputs=("rsi",),
        bounds={"rsi": (0.0, 100.0)},
        talib_compatible=True,
        references=("Wilder 1978", "TA-Lib RSI", "pandas-ta rsi"),
        doc="ref/ta_docs/momentum/RSI.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return rsi(df[CLOSE], self.params["length"])
