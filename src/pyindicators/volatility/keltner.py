"""Keltner Channels — volatility envelope using ATR (modern / Linda Raschke version).

``Middle = EMA(close, length)``; bands = Middle +/- mult * ATR(atr_length). Smoother than
Bollinger (which uses stdev). Composes ``base.ema`` + ``volatility.atr``.
See ``ref/ta_docs/volatility/Keltner.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec

from .atr import atr


def keltner(df: pd.DataFrame, length: int = 20, atr_length: int = 10, mult: float = 2.0) -> dict:
    """Keltner middle (EMA) and ATR-based upper/lower channels."""
    middle = ema(df[CLOSE], length)
    band = mult * atr(df, atr_length)
    return {"kc_lower": middle - band, "kc_middle": middle, "kc_upper": middle + band}


@INDICATORS.register
class Keltner(Indicator):
    """Keltner Channels (modern ATR version).

    What: an EMA with ATR-scaled bands; pairs with Bollinger for the "squeeze".
    Best settings: EMA 20, ATR 10, multiplier 2 (modern).
    Edge cases: inherits EMA + ATR warm-up; the original SMA/typical-price variant differs.
    Parity: pandas-ta ``kc`` family (variant-dependent); we implement the modern ATR version.
    """

    spec = IndicatorSpec(
        name="keltner",
        category="volatility",
        aliases=("Keltner Channels", "KC"),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("kc_lower", "kc_middle", "kc_upper"),
        references=("Keltner", "Raschke", "pandas-ta kc"),
        doc="ref/ta_docs/volatility/Keltner.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=1)
        atr_length: int = Field(default=10, ge=1)
        mult: float = Field(default=2.0, gt=0)

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return keltner(df, p["length"], p["atr_length"], p["mult"])
