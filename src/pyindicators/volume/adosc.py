"""Chaikin Oscillator (ADOSC) — momentum of the Accumulation/Distribution Line.

``ADOSC = EMA(ADL, fast) - EMA(ADL, slow)``. Composes ``volume.ad`` + ``base.ema``.
See ``ref/ta_docs/volume/ADL_CMF_Chaikin.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, VOLUME, Indicator, IndicatorSpec

from .ad import ad


def adosc(df: pd.DataFrame, fast: int = 3, slow: int = 10) -> pd.Series:
    """Chaikin Oscillator = EMA(ADL, fast) - EMA(ADL, slow)."""
    adl = ad(df)
    return ema(adl, fast) - ema(adl, slow)


@INDICATORS.register
class ChaikinOscillator(Indicator):
    """Chaikin Oscillator.

    What: the difference of two EMAs of the A/D Line — momentum of accumulation/distribution.
    Best settings: fast 3, slow 10.
    Edge cases: inherits EMA warm-up; converges to TA-Lib after the EMA seeding washes out.
    Parity: TA-Lib ``ADOSC`` / pandas-ta ``adosc`` (tail converges).
    """

    spec = IndicatorSpec(
        name="adosc",
        category="volume",
        aliases=("Chaikin Oscillator", "ADOSC"),
        inputs=(HIGH, LOW, CLOSE, VOLUME),
        outputs=("adosc",),
        talib_compatible=True,
        references=("Chaikin", "TA-Lib ADOSC", "pandas-ta adosc"),
        doc="ref/ta_docs/volume/ADL_CMF_Chaikin.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        fast: int = Field(default=3, ge=1)
        slow: int = Field(default=10, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return adosc(df, self.params["fast"], self.params["slow"])
