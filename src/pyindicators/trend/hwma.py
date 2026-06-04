"""HWMA — Holt-Winter Moving Average (triple-smoothing forecast).

A three-parameter smoother tracking level (F), velocity (V) and acceleration (A); the output is
``F + V + 0.5*A``. Implemented for MetaTrader 5 and ported by pandas-ta. Pure recursion seeded
with the first close. See ``ref/ta_docs/trend/misc_MA.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def hwma(close: pd.Series, na: float = 0.2, nb: float = 0.1, nc: float = 0.1) -> pd.Series:
    """Holt-Winter MA: level/velocity/acceleration smoothing with weights na/nb/nc."""
    x = close.to_numpy(dtype="float64")
    n = x.size
    out = np.empty(n)
    last_a = 0.0
    last_v = 0.0
    last_f = x[0] if n else 0.0
    for i in range(n):
        f = (1.0 - na) * (last_f + last_v + 0.5 * last_a) + na * x[i]
        v = (1.0 - nb) * (last_v + last_a) + nb * (f - last_f)
        a = (1.0 - nc) * last_a + nc * (v - last_v)
        out[i] = f + v + 0.5 * a
        last_a, last_f, last_v = a, f, v
    return pd.Series(out, index=close.index)


@INDICATORS.register
class HWMA(Indicator):
    """Holt-Winter Moving Average.

    What: a triple-smoothing MA modelling level, velocity and acceleration of price.
    Best settings: ``na`` 0.2, ``nb`` 0.1, ``nc`` 0.1 (each a smoothing weight in (0, 1)).
    Edge cases: starts at bar 0 (level seeded with the first close, velocity/accel 0); no
        warm-up NaN.
    Parity: pandas-ta ``hwma``, exact.
    """

    spec = IndicatorSpec(
        name="hwma",
        category="trend",
        aliases=("Holt-Winter Moving Average",),
        inputs=(CLOSE,),
        outputs=("hwma",),
        stateful=True,
        references=("Holt-Winter", "pandas-ta hwma"),
        doc="ref/ta_docs/trend/misc_MA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        na: float = Field(default=0.2, gt=0.0, lt=1.0)
        nb: float = Field(default=0.1, gt=0.0, lt=1.0)
        nc: float = Field(default=0.1, gt=0.0, lt=1.0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        p = self.params
        return hwma(df[CLOSE], p["na"], p["nb"], p["nc"])
