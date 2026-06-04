"""KVO — Klinger Volume Oscillator (Stephen Klinger).

Signs each bar's volume by whether the typical price (HLC3) rose or fell, then takes the spread
between a fast and slow EMA of that signed volume; a signal line is an EMA of the oscillator.
Designed to track long-term money flow while staying responsive to short-term turns. Composes
``base.ema``. See ``ref/ta_docs/volume/misc_volume.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, VOLUME, Indicator, IndicatorSpec


def kvo(df: pd.DataFrame, fast: int = 34, slow: int = 55, signal: int = 13) -> dict:
    """Klinger Volume Oscillator and its signal line."""
    hlc3 = (df[HIGH] + df[LOW] + df[CLOSE]) / 3.0
    signed = np.sign(hlc3.diff())  # +1 up day, -1 down day, 0 unchanged
    signed.iloc[0] = 1.0  # seed the first bar (matches pandas-ta's signed_series initial)
    sv = df[VOLUME] * signed
    line = ema(sv, fast) - ema(sv, slow)
    return {"kvo": line, "kvo_signal": ema(line, signal)}


@INDICATORS.register
class KVO(Indicator):
    """Klinger Volume Oscillator.

    What: long-term money-flow oscillator — fast minus slow EMA of volume signed by HLC3 trend.
    Best settings: 34/55/13; zero-line and signal crossovers flag accumulation/distribution.
    Edge cases: first bar's trend seeded +1; warm-up = slow + signal EMA lengths.
    Parity: pandas-ta ``kvo`` (EMA mamode).
    """

    spec = IndicatorSpec(
        name="kvo",
        category="volume",
        aliases=("Klinger Volume Oscillator", "Klinger"),
        inputs=(HIGH, LOW, CLOSE, VOLUME),
        outputs=("kvo", "kvo_signal"),
        references=("Klinger", "pandas-ta kvo"),
        doc="ref/ta_docs/volume/misc_volume.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        fast: int = Field(default=34, ge=1)
        slow: int = Field(default=55, ge=1)
        signal: int = Field(default=13, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return kvo(df, p["fast"], p["slow"], p["signal"])
