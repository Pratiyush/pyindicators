"""Aberration — an ATR channel around the typical price (a Keltner-like volatility band).

Middle = SMA of HLC3; the upper/lower bands are the middle plus/minus a (longer) ATR. Useful as
a mean-reversion / breakout envelope. Composes ``volatility.atr`` + ``price_transform.hlc3`` +
``base.sma``. See ``ref/ta_docs/volatility/misc_volatility.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec
from pyindicators.price_transform.hlc3 import hlc3
from pyindicators.volatility.atr import atr


def aberration(df: pd.DataFrame, length: int = 5, atr_length: int = 15) -> dict:
    """Aberration bands: SMA(HLC3) middle +/- ATR(atr_length)."""
    mid = sma(hlc3(df), length)
    band = atr(df, atr_length)
    return {
        "aber_zg": mid,
        "aber_sg": mid + band,
        "aber_xg": mid - band,
        "aber_atr": band,
    }


@INDICATORS.register
class Aberration(Indicator):
    """Aberration.

    What: an SMA(HLC3) midline with ATR-width upper/lower bands (a volatility envelope).
    Best settings: length 5, atr_length 15; price outside the bands flags stretch/breakout.
    Edge cases: warm-up = max(length, atr_length); bands inherit the ATR's Wilder warm-up.
    Parity: pandas-ta ``aberration`` — the SMA midline (ZG) matches exactly; the ATR-based
        bands (SG/XG/ATR) converge on the tail (Wilder seed), like ATR itself.
    """

    spec = IndicatorSpec(
        name="aberration",
        category="volatility",
        aliases=("Aberration", "ABER"),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("aber_zg", "aber_sg", "aber_xg", "aber_atr"),
        references=("pandas-ta aberration",),
        doc="ref/ta_docs/volatility/misc_volatility.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=5, ge=1)
        atr_length: int = Field(default=15, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return aberration(df, p["length"], p["atr_length"])
