"""Ultimate Oscillator (UO) — multi-timeframe momentum (Larry Williams 1976).

Combines buying-pressure/true-range ratios over three windows (weighted 4/2/1) to reduce
false divergences. ``BP = Close - min(Low, prevClose)``; ``TR = max(High, prevClose) -
min(Low, prevClose)``. See ``ref/ta_docs/momentum/UltimateOscillator.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec, safe_divide


def uo(
    df: pd.DataFrame,
    fast: int = 7,
    medium: int = 14,
    slow: int = 28,
    fast_w: float = 4.0,
    medium_w: float = 2.0,
    slow_w: float = 1.0,
) -> pd.Series:
    """Ultimate Oscillator (0-100) across three windows."""
    prev_close = df[CLOSE].shift(1)
    low_or_pc = pd.concat([df[LOW], prev_close], axis=1).min(axis=1)
    high_or_pc = pd.concat([df[HIGH], prev_close], axis=1).max(axis=1)
    bp = df[CLOSE] - low_or_pc
    tr = high_or_pc - low_or_pc
    bp.iloc[0] = np.nan  # no prior close on the first bar (exclude from the sums)
    tr.iloc[0] = np.nan

    def avg(n: int) -> pd.Series:
        return safe_divide(
            bp.rolling(n, min_periods=n).sum(), tr.rolling(n, min_periods=n).sum()
        )

    weighted = fast_w * avg(fast) + medium_w * avg(medium) + slow_w * avg(slow)
    return 100.0 * weighted / (fast_w + medium_w + slow_w)


@INDICATORS.register
class UltimateOscillator(Indicator):
    """Ultimate Oscillator.

    What: weighted buying-pressure momentum across 3 timeframes (0-100); used for divergence.
    Best settings: 7/14/28, weights 4/2/1 (Williams); >70 overbought, <30 oversold.
    Edge cases: sum(TR) == 0 (flat, no gaps) -> guarded to NaN.
    Parity: TA-Lib ``ULTOSC`` / pandas-ta ``uo``.
    """

    spec = IndicatorSpec(
        name="uo",
        category="momentum",
        aliases=("Ultimate Oscillator",),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("uo",),
        bounds={"uo": (0.0, 100.0)},
        talib_compatible=True,
        references=("Williams 1976", "TA-Lib ULTOSC", "pandas-ta uo"),
        doc="ref/ta_docs/momentum/UltimateOscillator.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        fast: int = Field(default=7, ge=1)
        medium: int = Field(default=14, ge=1)
        slow: int = Field(default=28, ge=1)
        fast_w: float = Field(default=4.0, gt=0)
        medium_w: float = Field(default=2.0, gt=0)
        slow_w: float = Field(default=1.0, gt=0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        p = self.params
        return uo(df, p["fast"], p["medium"], p["slow"], p["fast_w"], p["medium_w"], p["slow_w"])
