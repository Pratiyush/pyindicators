"""KST — Know Sure Thing (Martin Pring's summed Rate-of-Change).

A smoothed, weighted sum of four ROCs across horizons: a long-term momentum oscillator.
``KST = 1*SMA(ROC10,10) + 2*SMA(ROC15,10) + 3*SMA(ROC20,10) + 4*SMA(ROC30,15)``; signal =
SMA(KST, 9). Composes ``momentum.roc`` + ``base.sma``. See ``ref/ta_docs/trend/KST.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec
from pyindicators.momentum.roc import roc


def kst(close: pd.Series, signal: int = 9) -> dict:
    """Pring's KST and its signal line (default ROC 10/15/20/30, SMA 10/10/10/15)."""
    rcma1 = sma(roc(close, 10), 10)
    rcma2 = sma(roc(close, 15), 10)
    rcma3 = sma(roc(close, 20), 10)
    rcma4 = sma(roc(close, 30), 15)
    line = 1.0 * rcma1 + 2.0 * rcma2 + 3.0 * rcma3 + 4.0 * rcma4
    return {"kst": line, "kst_signal": sma(line, signal)}


@INDICATORS.register
class KST(Indicator):
    """Know Sure Thing.

    What: a weighted sum of four smoothed ROCs — a long-term momentum oscillator.
    Best settings: Pring's ROC 10/15/20/30, SMA 10/10/10/15, signal 9 (daily).
    Edge cases: long warm-up (longest ROC + its SMA, ~45 bars).
    Parity: pandas-ta ``kst`` (not in core TA-Lib).
    """

    spec = IndicatorSpec(
        name="kst",
        category="trend",
        aliases=("Know Sure Thing", "Summed ROC"),
        inputs=(CLOSE,),
        outputs=("kst", "kst_signal"),
        references=("Pring", "pandas-ta kst"),
        doc="ref/ta_docs/trend/KST.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        signal: int = Field(default=9, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        return kst(df[CLOSE], self.params["signal"])
