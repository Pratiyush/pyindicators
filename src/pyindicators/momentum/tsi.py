"""TSI — True Strength Index (William Blau).

Double-smoothed price momentum normalised to [-100, 100]:
``TSI = 100 * EMA(EMA(pc, long), short) / EMA(EMA(|pc|, long), short)`` where pc = close diff.
Composes ``base.ema``. See ``ref/ta_docs/momentum/TSI.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide


def tsi(close: pd.Series, long: int = 25, short: int = 13, signal: int = 7) -> dict:
    """True Strength Index line and signal line."""
    pc = close.diff()
    pcds = ema(ema(pc, long), short)
    apcds = ema(ema(pc.abs(), long), short)
    line = 100.0 * safe_divide(pcds, apcds)  # |pcds| <= apcds, so line is in [-100, 100]
    return {"tsi": line, "tsi_signal": ema(line, signal)}


@INDICATORS.register
class TSI(Indicator):
    """True Strength Index.

    What: double-smoothed momentum in [-100, 100]; zero-line / signal crosses, divergence.
    Best settings: long 25, short 13, signal 7 (Blau); +/-25 cutoffs common.
    Edge cases: |momentum| EMA 0 (flat) -> guarded to NaN.
    Parity: pandas-ta ``tsi`` (not in core TA-Lib).
    """

    spec = IndicatorSpec(
        name="tsi",
        category="momentum",
        aliases=("True Strength Index",),
        inputs=(CLOSE,),
        outputs=("tsi", "tsi_signal"),
        bounds={"tsi": (-100.0, 100.0), "tsi_signal": (-100.0, 100.0)},
        references=("Blau", "pandas-ta tsi"),
        doc="ref/ta_docs/momentum/TSI.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        long: int = Field(default=25, ge=1)
        short: int = Field(default=13, ge=1)
        signal: int = Field(default=7, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return tsi(df[CLOSE], p["long"], p["short"], p["signal"])
