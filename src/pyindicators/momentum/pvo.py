"""PVO — Percentage Volume Oscillator (volume momentum).

PPO applied to volume: the percentage spread between a fast and slow EMA of volume, with a
signal line and histogram. Flags volume expansions/contractions independent of price.
``PVO = 100 * (EMA(vol, fast) - EMA(vol, slow)) / EMA(vol, slow)``. Composes ``base.ema``.
See ``ref/ta_docs/momentum/misc_momentum.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import INDICATORS, VOLUME, Indicator, IndicatorSpec, safe_divide


def pvo(
    volume: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
    talib_compatible: bool = True,
) -> dict:
    """Percentage Volume Oscillator line, signal, and histogram."""
    ef = ema(volume, fast, talib_compatible)
    es = ema(volume, slow, talib_compatible)
    line = 100.0 * safe_divide(ef - es, es)
    signal_line = ema(line, signal, talib_compatible)
    return {"pvo": line, "pvo_signal": signal_line, "pvo_hist": line - signal_line}


@INDICATORS.register
class PVO(Indicator):
    """Percentage Volume Oscillator.

    What: MACD/PPO computed on volume — a normalised gauge of volume momentum.
    Best settings: 12/26/9; PVO > 0 = volume rising (fast EMA above slow), histogram = impulse.
    Edge cases: slow EMA 0 (no volume) -> guarded; warm-up = slow + signal.
    Parity: pandas-ta ``pvo`` (clean SMA-seeded EMAs).
    """

    spec = IndicatorSpec(
        name="pvo",
        category="momentum",
        aliases=("Percentage Volume Oscillator",),
        inputs=(VOLUME,),
        outputs=("pvo", "pvo_signal", "pvo_hist"),
        talib_compatible=True,
        references=("pandas-ta pvo",),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        fast: int = Field(default=12, ge=1)
        slow: int = Field(default=26, ge=1)
        signal: int = Field(default=9, ge=1)
        talib_compatible: bool = True

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return pvo(df[VOLUME], p["fast"], p["slow"], p["signal"], p["talib_compatible"])
