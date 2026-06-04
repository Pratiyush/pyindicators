"""Chandelier Exit — ATR trailing stops (Chuck LeBeau).

``Long stop = HH(N) - mult*ATR``; ``Short stop = LL(N) + mult*ATR``. Composes
``volatility.atr``. See ``ref/ta_docs/volatility/misc_volatility.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec

from .atr import atr


def chandelier(df: pd.DataFrame, length: int = 22, mult: float = 3.0, atr_length: int = 22) -> dict:
    """Chandelier Exit long/short trailing-stop levels."""
    a = mult * atr(df, atr_length)
    hh = df[HIGH].rolling(length, min_periods=length).max()
    ll = df[LOW].rolling(length, min_periods=length).min()
    return {"chandelier_long": hh - a, "chandelier_short": ll + a}


@INDICATORS.register
class ChandelierExit(Indicator):
    """Chandelier Exit.

    What: ATR-based trailing stops below the recent high (long) and above the recent low (short).
    Best settings: ``length`` 22, ``mult`` 3, ATR 22 (LeBeau).
    Edge cases: inherits ATR warm-up.
    Parity: standard Chandelier Exit formula (validated structurally: long < HH, short > LL).
    """

    spec = IndicatorSpec(
        name="chandelier",
        category="volatility",
        aliases=("Chandelier Exit", "CE"),
        inputs=(HIGH, LOW, "close"),
        outputs=("chandelier_long", "chandelier_short"),
        references=("LeBeau", "standard Chandelier Exit"),
        doc="ref/ta_docs/volatility/misc_volatility.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=22, ge=1)
        mult: float = Field(default=3.0, gt=0)
        atr_length: int = Field(default=22, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return chandelier(df, p["length"], p["mult"], p["atr_length"])
