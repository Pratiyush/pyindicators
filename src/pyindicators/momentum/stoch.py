"""Stochastic Oscillator (%K / %D) — momentum (George Lane).

Where the close sits within the recent high-low range, scaled 0-100, then smoothed. This is
the *slow* stochastic by default (raw %K smoothed by ``smooth_k`` -> slow %K; %D = SMA of
slow %K). Composes ``base.sma``. See ``ref/ta_docs/momentum/Stochastic.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec, safe_divide


def stoch(df: pd.DataFrame, k: int = 14, d: int = 3, smooth_k: int = 3) -> dict:
    """Slow Stochastic: returns smoothed %K and %D (both 0-100)."""
    ll = df[LOW].rolling(k, min_periods=k).min()
    hh = df[HIGH].rolling(k, min_periods=k).max()
    raw_k = safe_divide(100.0 * (df[CLOSE] - ll), hh - ll)  # NaN where HH == LL
    slow_k = sma(raw_k, smooth_k)
    slow_d = sma(slow_k, d)
    return {"stoch_k": slow_k, "stoch_d": slow_d}


@INDICATORS.register
class Stochastic(Indicator):
    """Stochastic Oscillator (slow %K / %D).

    What: position of close within the N-bar range (0-100), smoothed.
    Best settings: 14/3/3 (slow); 5/3/3 for faster signals; bands 80/20.
    Edge cases: HH == LL (flat window) -> %K undefined -> guarded to NaN.
    Parity: TA-Lib ``STOCH`` (slowk/slowd, SMA smoothing) / pandas-ta ``stoch``.
    """

    spec = IndicatorSpec(
        name="stoch",
        category="momentum",
        aliases=("Stochastic Oscillator", "%K/%D"),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("stoch_k", "stoch_d"),
        bounds={"stoch_k": (0.0, 100.0), "stoch_d": (0.0, 100.0)},
        talib_compatible=True,
        references=("Lane", "TA-Lib STOCH", "pandas-ta stoch"),
        doc="ref/ta_docs/momentum/Stochastic.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        k: int = Field(default=14, ge=1)
        d: int = Field(default=3, ge=1)
        smooth_k: int = Field(default=3, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        return stoch(df, self.params["k"], self.params["d"], self.params["smooth_k"])
