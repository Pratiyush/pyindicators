"""Stochastic RSI — a stochastic applied to RSI (Chande & Kroll 1994).

A faster, more sensitive overbought/oversold oscillator: normalise RSI over its own N-bar
range, then smooth. Composes ``momentum.rsi`` + ``base.sma``. See ``ref/ta_docs/momentum/StochRSI.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide

from .rsi import rsi


def stochrsi(close: pd.Series, rsi_length: int = 14, length: int = 14, k: int = 3, d: int = 3) -> dict:
    """Stochastic RSI %K and %D (0-100)."""
    r = rsi(close, rsi_length)
    ll = r.rolling(length, min_periods=length).min()
    hh = r.rolling(length, min_periods=length).max()
    raw = 100.0 * safe_divide(r - ll, hh - ll)  # NaN where RSI is flat over the window
    k_line = sma(raw, k)
    return {"stochrsi_k": k_line, "stochrsi_d": sma(k_line, d)}


@INDICATORS.register
class StochRSI(Indicator):
    """Stochastic RSI.

    What: a stochastic of the RSI series — a fast overbought/oversold oscillator (0-100).
    Best settings: 14/14/3/3 (classic); >80 overbought, <20 oversold.
    Edge cases: max(RSI) == min(RSI) over the window -> guarded to NaN; double warm-up.
    Parity: pandas-ta ``stochrsi`` (same RSI->stoch->%K/%D structure).
    """

    spec = IndicatorSpec(
        name="stochrsi",
        category="momentum",
        aliases=("Stochastic RSI",),
        inputs=(CLOSE,),
        outputs=("stochrsi_k", "stochrsi_d"),
        bounds={"stochrsi_k": (0.0, 100.0), "stochrsi_d": (0.0, 100.0)},
        references=("Chande & Kroll 1994", "TA-Lib STOCHRSI", "pandas-ta stochrsi"),
        doc="ref/ta_docs/momentum/StochRSI.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        rsi_length: int = Field(default=14, ge=1)
        length: int = Field(default=14, ge=1)
        k: int = Field(default=3, ge=1)
        d: int = Field(default=3, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return stochrsi(df[CLOSE], p["rsi_length"], p["length"], p["k"], p["d"])
