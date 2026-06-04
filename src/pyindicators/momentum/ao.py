"""AO — Awesome Oscillator (Bill Williams): ``SMA(hl2, 5) - SMA(hl2, 34)`` (momentum)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def ao(df: pd.DataFrame, fast: int = 5, slow: int = 34) -> pd.Series:
    """Awesome Oscillator = SMA(hl2, fast) - SMA(hl2, slow)."""
    hl2 = (df[HIGH] + df[LOW]) / 2.0
    return sma(hl2, fast) - sma(hl2, slow)


@INDICATORS.register
class AwesomeOscillator(Indicator):
    """Awesome Oscillator.

    What: difference of two SMAs of the median price — broad market momentum.
    Best settings: fast 5, slow 34 (Williams); zero-line and saucer signals.
    Edge cases: warm-up = slow length.
    Parity: pandas-ta ``ao`` (not in core TA-Lib).
    """

    spec = IndicatorSpec(
        name="ao",
        category="momentum",
        aliases=("Awesome Oscillator",),
        inputs=(HIGH, LOW),
        outputs=("ao",),
        references=("Bill Williams", "pandas-ta ao"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        fast: int = Field(default=5, ge=1)
        slow: int = Field(default=34, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return ao(df, self.params["fast"], self.params["slow"])
