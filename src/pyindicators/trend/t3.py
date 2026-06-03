"""T3 — Tillson T3 Moving Average (low-lag, Tim Tillson 1998).

A 6-fold EMA cascade combined with a volume factor ``v`` (default 0.7) into a smooth,
low-lag line: ``T3 = c1*e6 + c2*e5 + c3*e4 + c4*e3`` with coefficients derived from ``v``.
Composes ``base.ema``. See ``ref/ta_docs/trend/misc_MA.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def t3(close: pd.Series, length: int = 5, vfactor: float = 0.7, talib_compatible: bool = True) -> pd.Series:
    """Tillson T3 over ``length`` with volume factor ``vfactor`` (6 nested EMAs)."""
    e1 = ema(close, length, talib_compatible)
    e2 = ema(e1, length, talib_compatible)
    e3 = ema(e2, length, talib_compatible)
    e4 = ema(e3, length, talib_compatible)
    e5 = ema(e4, length, talib_compatible)
    e6 = ema(e5, length, talib_compatible)
    a = vfactor
    c1 = -(a**3)
    c2 = 3 * a**2 + 3 * a**3
    c3 = -6 * a**2 - 3 * a - 3 * a**3
    c4 = 1 + 3 * a + a**3 + 3 * a**2
    return c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3


@INDICATORS.register
class T3(Indicator):
    """Tillson T3 Moving Average.

    What: a very smooth, low-lag MA from a 6-EMA cascade weighted by a volume factor.
    Best settings: ``length`` 5, ``vfactor`` 0.7 (Tillson); larger length = smoother.
    Edge cases: very long warm-up (~6*length); inherits EMA seeding.
    Parity: TA-Lib ``T3`` / pandas-ta ``t3``.
    """

    spec = IndicatorSpec(
        name="t3",
        category="trend",
        aliases=("Tillson T3",),
        inputs=(CLOSE,),
        outputs=("t3",),
        talib_compatible=True,
        references=("Tillson 1998", "TA-Lib T3", "pandas-ta t3"),
        doc="ref/ta_docs/trend/misc_MA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=5, ge=1)
        vfactor: float = Field(default=0.7, ge=0, le=1)
        talib_compatible: bool = True

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        p = self.params
        return t3(df[CLOSE], p["length"], p["vfactor"], p["talib_compatible"])
