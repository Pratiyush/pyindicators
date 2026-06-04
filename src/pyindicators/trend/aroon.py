"""Aroon & Aroon Oscillator — trend freshness (Tushar Chande 1995).

Measures how recently the highest high / lowest low occurred within the lookback.
``AroonUp = 100 * (N - bars_since_HH) / N``; the oscillator is Up - Down. Uses a window of
``length + 1`` bars to match TA-Lib. See ``ref/ta_docs/trend/Aroon.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def _bars_since_extreme_last(w: np.ndarray, extreme: str) -> float:
    """Window position of the MOST-RECENT high/low (ties resolve to the latest bar, per TA-Lib)."""
    rev = w[::-1]
    idx = np.argmax(rev) if extreme == "high" else np.argmin(rev)
    return float(len(w) - 1 - idx)  # last occurrence in the original window


def aroon(df: pd.DataFrame, length: int = 25) -> dict:
    """Aroon Down, Up, and Oscillator over ``length`` bars."""
    win = length + 1  # TA-Lib looks over the current bar + the previous `length`
    up = df[HIGH].rolling(win, min_periods=win).apply(
        lambda w: 100.0 * _bars_since_extreme_last(w, "high") / length, raw=True
    )
    down = df[LOW].rolling(win, min_periods=win).apply(
        lambda w: 100.0 * _bars_since_extreme_last(w, "low") / length, raw=True
    )
    return {"aroon_down": down, "aroon_up": up, "aroon_osc": up - down}


@INDICATORS.register
class Aroon(Indicator):
    """Aroon & Aroon Oscillator.

    What: how fresh the period high/low is — Up/Down each 0-100, oscillator -100..+100.
    Best settings: ``length`` 25 (Chande); 14 for faster.
    Edge cases: ties resolve to the most-recent extreme (argmax/argmin on the window).
    Parity: TA-Lib ``AROON`` / ``AROONOSC`` / pandas-ta ``aroon``.
    """

    spec = IndicatorSpec(
        name="aroon",
        category="trend",
        aliases=("Aroon", "Aroon Oscillator"),
        inputs=(HIGH, LOW),
        outputs=("aroon_down", "aroon_up", "aroon_osc"),
        bounds={"aroon_down": (0.0, 100.0), "aroon_up": (0.0, 100.0), "aroon_osc": (-100.0, 100.0)},
        talib_compatible=True,
        references=("Chande 1995", "TA-Lib AROON", "pandas-ta aroon"),
        doc="ref/ta_docs/trend/Aroon.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=25, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        return aroon(df, self.params["length"])
