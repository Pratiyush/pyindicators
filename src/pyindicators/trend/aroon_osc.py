"""Aroon Oscillator — AroonUp minus AroonDown (Tushar Chande 1995).

A single -100..+100 line: positive when the period high is fresher than the period low
(up-trend), negative otherwise. Composes :func:`aroon`. See ``ref/ta_docs/trend/Aroon.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec

from .aroon import aroon


def aroon_osc(df: pd.DataFrame, length: int = 25) -> pd.Series:
    """Aroon Oscillator: AroonUp - AroonDown over ``length`` bars (-100..+100)."""
    return aroon(df, length)["aroon_osc"]


@INDICATORS.register
class AroonOscillator(Indicator):
    """Aroon Oscillator.

    What: AroonUp - AroonDown — a single line gauging trend direction and freshness.
    Best settings: ``length`` 25 (Chande); > 0 up-trend, < 0 down-trend, near 0 = range.
    Edge cases: first ``length`` bars NaN; ties resolve to the most-recent extreme.
    Parity: TA-Lib ``AROONOSC`` / pandas-ta ``aroon`` (oscillator column).
    """

    spec = IndicatorSpec(
        name="aroon_osc",
        category="trend",
        aliases=("Aroon Oscillator", "AROONOSC"),
        inputs=(HIGH, LOW),
        outputs=("aroon_osc",),
        bounds={"aroon_osc": (-100.0, 100.0)},
        talib_compatible=True,
        references=("Chande 1995", "TA-Lib AROONOSC", "pandas-ta aroon"),
        doc="ref/ta_docs/trend/Aroon.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=25, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return aroon_osc(df, self.params["length"])
