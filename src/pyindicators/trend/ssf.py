"""SSF — Ehlers' Super Smoother Filter (John F. Ehlers, 2013).

A Butterworth-style recursive digital filter that removes aliasing noise with far less lag than
a moving average. ``poles=2`` uses the two prior SSF bars; ``poles=3`` uses three. Seeded with
the raw closes for the first ``poles`` bars. See ``ref/ta_docs/trend/misc_MA.md``.
"""

from __future__ import annotations

import math
from typing import Literal

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def ssf(close: pd.Series, length: int = 10, poles: Literal[2, 3] = 2) -> pd.Series:
    """Ehlers Super Smoother Filter (2- or 3-pole recursive low-pass)."""
    out = close.to_numpy(dtype="float64").copy()
    x = out.copy()
    n = x.size
    if poles == 3:
        a = math.pi / length
        a0 = math.exp(-a)
        b0 = 2.0 * a0 * math.cos(math.sqrt(3.0) * a)
        c0 = a0 * a0
        c4 = c0 * c0
        c3 = -c0 * (1.0 + b0)
        c2 = c0 + b0
        c1 = 1.0 - c2 - c3 - c4
        for i in range(3, n):
            out[i] = c1 * x[i] + c2 * out[i - 1] + c3 * out[i - 2] + c4 * out[i - 3]
    else:  # poles == 2
        a = math.pi * math.sqrt(2.0) / length
        a0 = math.exp(-a)
        a1 = -a0 * a0
        b1 = 2.0 * a0 * math.cos(a)
        c1 = 1.0 - a1 - b1
        for i in range(2, n):
            out[i] = c1 * x[i] + b1 * out[i - 1] + a1 * out[i - 2]
    return pd.Series(out, index=close.index)


@INDICATORS.register
class SuperSmoother(Indicator):
    """Ehlers' Super Smoother Filter.

    What: a recursive low-pass filter that smooths price with minimal lag and no aliasing.
    Best settings: ``length`` 10; ``poles`` 2 (default) or 3 (sharper roll-off, more lag).
    Edge cases: the first ``poles`` bars pass through unchanged (filter seed); frames shorter
        than ``poles`` are returned as the raw close.
    Parity: pandas-ta ``ssf``, exact.
    """

    spec = IndicatorSpec(
        name="ssf",
        category="trend",
        aliases=("Super Smoother Filter", "Ehlers SSF"),
        inputs=(CLOSE,),
        outputs=("ssf",),
        stateful=True,
        references=("Ehlers 2013", "pandas-ta ssf"),
        doc="ref/ta_docs/trend/misc_MA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=10, ge=1)
        poles: Literal[2, 3] = 2

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        p = self.params
        return ssf(df[CLOSE], p["length"], p["poles"])
