"""Composite Index (Constance Brown) — an unbound RSI derivative that fixes RSI's range cap.

``CI = momentum(RSI(rsi_length), momentum_length) + SMA(RSI(short_rsi), short_sma)``.
Composes ``momentum.rsi`` + ``base.sma``. See ``ref/ta_docs/momentum/misc_momentum.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from .rsi import rsi


def cmb_composite_index(
    close: pd.Series,
    rsi_length: int = 14,
    momentum_length: int = 9,
    short_rsi: int = 3,
    short_sma: int = 3,
) -> pd.Series:
    """Brown's Composite Index: RSI momentum plus a smoothed short RSI (unbounded)."""
    rsi_momentum = rsi(close, rsi_length).diff(momentum_length)
    smoothed_short = sma(rsi(close, short_rsi), short_sma)
    return rsi_momentum + smoothed_short


@INDICATORS.register
class CompositeIndex(Indicator):
    """Composite Index (Constance Brown).

    What: an unbounded RSI-derivative that surfaces divergences RSI's 0-100 cap can hide.
    Best settings: RSI 14, momentum 9, short RSI 3, short SMA 3.
    Edge cases: inherits RSI warm-up; unbounded.
    Parity: Brown's formula (validated against the explicit definition; no single library oracle).
    """

    spec = IndicatorSpec(
        name="cmb_composite_index",
        category="momentum",
        aliases=("Composite Index", "Brown Composite Index"),
        inputs=(CLOSE,),
        outputs=("cmb_composite_index",),
        references=("Constance Brown, TA for the Trading Professional",),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        rsi_length: int = Field(default=14, ge=1)
        momentum_length: int = Field(default=9, ge=1)
        short_rsi: int = Field(default=3, ge=1)
        short_sma: int = Field(default=3, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        p = self.params
        return cmb_composite_index(
            df[CLOSE], p["rsi_length"], p["momentum_length"], p["short_rsi"], p["short_sma"]
        )
