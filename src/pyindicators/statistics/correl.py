"""CORREL — rolling Pearson correlation coefficient of two series (statistics).

Pearson's r between ``high`` and ``low`` over a trailing window of ``length`` bars: how
tightly the two move together (1 = perfectly together, -1 = perfectly opposed, 0 = none).
Computed with pandas' rolling ``corr`` (the scale factor in numerator/denominator cancels,
so sample-vs-population ddof is irrelevant). Result is clamped into ``[-1, 1]`` to absorb the
~1e-15 floating-point overshoot that exact-correlation windows produce. See
``ref/ta_docs/statistics/misc_statistics.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec, clamp


def correl(high: pd.Series, low: pd.Series, length: int = 30) -> pd.Series:
    """Rolling Pearson correlation of ``high`` & ``low`` over ``length`` bars, in [-1, 1].

    A window with zero variance in either series has an undefined correlation (0/0): pandas
    yields NaN, which we keep rather than fabricate (TA-Lib emits 0.0 there — a documented
    convention difference; real OHLCV high/low never go flat for a whole window).
    """
    r = high.rolling(length, min_periods=length).corr(low)
    return clamp(r, -1.0, 1.0)


@INDICATORS.register
class Correl(Indicator):
    """Pearson Correlation Coefficient (rolling).

    What: trailing Pearson r between high and low (co-movement of the bar's range extremes).
    Best settings: ``length`` 30 (TA-Lib default); near 1 = orderly trend, dips = choppiness.
    Edge cases: a flat (zero-variance) window -> 0/0 -> NaN; output clamped to [-1, 1].
    Parity: TA-Lib ``CORREL`` (rolling Pearson; differs only on flat windows -> NaN vs 0).
    """

    spec = IndicatorSpec(
        name="correl",
        category="statistics",
        aliases=("Pearson Correlation Coefficient", "CORREL"),
        inputs=(HIGH, LOW),
        outputs=("correl",),
        bounds={"correl": (-1.0, 1.0)},
        talib_compatible=True,
        references=("TA-Lib CORREL", "pandas-ta correl"),
        doc="ref/ta_docs/statistics/misc_statistics.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=30, ge=2)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return correl(df[HIGH], df[LOW], self.params["length"])
