"""KAMA — Kaufman's Adaptive Moving Average (Perry Kaufman).

A moving average that speeds up in efficient (trending) markets and slows in noisy ones via
an Efficiency Ratio. The smoothing constant is SQUARED (the #1 implementation bug is
forgetting the square). Stateful recursion. See ``ref/ta_docs/trend/KAMA.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def kama(close: pd.Series, length: int = 10, fast: int = 2, slow: int = 30) -> pd.Series:
    """Kaufman Adaptive MA: ER over ``length``; SC = (ER*(fastest-slowest)+slowest)^2."""
    x = close.to_numpy(dtype="float64")
    n = x.size
    out = np.full(n, np.nan)
    if n < length:
        return pd.Series(out, index=close.index)
    fastest = 2.0 / (fast + 1.0)
    slowest = 2.0 / (slow + 1.0)
    abs_diff = np.abs(np.diff(x, prepend=x[0]))  # abs_diff[0] == 0
    volatility = pd.Series(abs_diff).rolling(length).sum().to_numpy()
    out[length - 1] = x[length - 1]  # seed prevKAMA with the price at the warm-up boundary
    for i in range(length, n):
        change = abs(x[i] - x[i - length])
        vol = volatility[i]
        er = change / vol if vol != 0 else 0.0  # flat window -> ER 0 -> SC = slowest^2
        sc = (er * (fastest - slowest) + slowest) ** 2
        out[i] = out[i - 1] + sc * (x[i] - out[i - 1])
    return pd.Series(out, index=close.index)


@INDICATORS.register
class KAMA(Indicator):
    """Kaufman's Adaptive Moving Average.

    What: an MA that tracks price closely in trends and flattens in chop (ER-driven).
    Best settings: er=10, fast=2, slow=30 (Kaufman). Flat KAMA = stand aside.
    Edge cases: volatility 0 (constant price) -> ER 0 -> SC = slowest^2; first ``length`` bars NaN.
    Parity: TA-Lib ``KAMA`` (timeperiod=er; fast/slow fixed 2/30) — converges on the tail.
    """

    spec = IndicatorSpec(
        name="kama",
        category="trend",
        aliases=("Kaufman Adaptive MA",),
        inputs=(CLOSE,),
        outputs=("kama",),
        stateful=True,
        references=("Kaufman", "TA-Lib KAMA", "pandas-ta kama"),
        doc="ref/ta_docs/trend/KAMA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=10, ge=1)
        fast: int = Field(default=2, ge=1)
        slow: int = Field(default=30, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        p = self.params
        return kama(df[CLOSE], p["length"], p["fast"], p["slow"])
