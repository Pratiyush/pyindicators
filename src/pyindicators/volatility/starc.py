"""STARC Bands — Stoller Average Range Channel (volatility envelope, Manning Stoller).

An SMA of close with bands set at +/- ``mult`` * ATR: ``Middle = SMA(close, ma_length)``;
``Upper/Lower = Middle +/- mult * ATR(atr_length)``. Like Keltner but the basis is a *simple*
moving average (not an EMA) and the ATR window is typically longer than the SMA window — the
channel widens with volatility while the centre tracks a short, responsive average. Composes
``base.sma`` + ``volatility.atr`` (never re-inlines the SMA/ATR/RMA math).
See ``ref/ta_docs/volatility/Keltner.md`` for the sibling ATR-envelope.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec

from .atr import atr


def starc(
    df: pd.DataFrame, ma_length: int = 5, atr_length: int = 15, mult: float = 2.0
) -> dict:
    """STARC middle (SMA of close) and ATR-scaled upper/lower bands.

    The middle is a plain ``SMA(close, ma_length)``; the half-width is ``mult * ATR(atr_length)``
    (Wilder-smoothed true range). The two warm-ups are independent, so a band value is finite
    only once *both* its SMA and ATR terms are finite (the later of ``ma_length`` /
    ``atr_length`` bars).
    """
    middle = sma(df[CLOSE], ma_length)
    band = mult * atr(df, atr_length)  # ATR is purely additive here; no division to guard
    return {
        "starc_middle": middle,
        "starc_upper": middle + band,
        "starc_lower": middle - band,
    }


@INDICATORS.register
class STARC(Indicator):
    """STARC Bands (Stoller Average Range Channel).

    What: an SMA basis with ATR-scaled bands; a Keltner cousin whose centre is a *simple* MA
        and whose ATR window is usually longer than the MA window.
    Best settings: SMA 5, ATR 15, multiplier 2 (Stoller); widen ``mult`` to throttle signals.
    Edge cases: a band needs both warm-ups (max of ma_length / atr_length); flat market ->
        ATR 0 -> the three lines coincide.
    Parity: no library oracle exists; verified against ``SMA(close) +/- mult * ATR`` built from
        the reference lib's own SMA/ATR. Middle matches SMA exactly; bands use tail+rtol because
        ATR's Wilder seed converges (pandas-ta NaNs the first true range, we use H-L at bar 0).
    """

    spec = IndicatorSpec(
        name="starc",
        category="volatility",
        aliases=("STARC Bands", "Stoller Average Range Channel"),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("starc_middle", "starc_upper", "starc_lower"),
        references=("Manning Stoller", "SMA +/- mult*ATR", "pandas-ta sma/atr"),
        doc="ref/ta_docs/volatility/Keltner.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        ma_length: int = Field(default=5, ge=1)
        atr_length: int = Field(default=15, ge=1)
        mult: float = Field(default=2.0, gt=0)

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return starc(df, p["ma_length"], p["atr_length"], p["mult"])
