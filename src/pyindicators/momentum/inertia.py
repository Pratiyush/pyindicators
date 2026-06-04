"""Inertia — a smoothed Relative Volatility Index (Donald Dorsey).

Inertia is the linear-regression (LSMA) of the RVI: it takes Dorsey's Relative Volatility Index
and fits a least-squares line through it, giving a slow, steady trend gauge — above 50 = bullish
inertia, below 50 = bearish. Composes ``volatility.rvi`` + ``statistics.linreg``. See
``ref/ta_docs/momentum/misc_momentum.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec
from pyindicators.statistics.linreg import linreg
from pyindicators.volatility.rvi import rvi


def inertia(close: pd.Series, length: int = 20, rvi_length: int = 14) -> pd.Series:
    """Inertia: linear-regression (LSMA) of RVI(close, rvi_length) over ``length`` bars."""
    return linreg(rvi(close, rvi_length), length)


@INDICATORS.register
class Inertia(Indicator):
    """Inertia.

    What: the LSMA (linear-regression) of the Relative Volatility Index — a slow trend gauge.
    Best settings: length 20, rvi_length 14; > 50 bullish inertia, < 50 bearish.
    Edge cases: warm-up = RVI warm-up + linreg length; inherits RVI's flat-window NaN.
    Parity: pandas-ta ``inertia`` (default close/EMA RVI mode).
    """

    spec = IndicatorSpec(
        name="inertia",
        category="momentum",
        aliases=("Inertia",),
        inputs=(CLOSE,),
        outputs=("inertia",),
        references=("Dorsey", "pandas-ta inertia"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=2)
        rvi_length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        p = self.params
        return inertia(df[CLOSE], p["length"], p["rvi_length"])
