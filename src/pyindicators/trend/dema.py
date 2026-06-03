"""DEMA — Double Exponential Moving Average (low-lag, Patrick Mulloy 1994).

A lag-cancelling combination of nested EMAs (NOT a 2x EMA): ``DEMA = 2*EMA - EMA(EMA)``.
Composes ``base.ema`` (seeding flows through both layers). See ``ref/ta_docs/trend/DEMA_TEMA.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def dema(close: pd.Series, length: int = 20, talib_compatible: bool = True) -> pd.Series:
    """Double EMA = 2*EMA(close) - EMA(EMA(close))."""
    e1 = ema(close, length, talib_compatible)
    e2 = ema(e1, length, talib_compatible)
    return 2.0 * e1 - e2


@INDICATORS.register
class DEMA(Indicator):
    """Double Exponential Moving Average.

    What: a reduced-lag smoother from a lag-cancelling EMA combination.
    Best settings: ``length`` 20 (smaller = faster, more overshoot).
    Edge cases: long warm-up (~2*length); inherits the EMA seeding convention.
    Parity: TA-Lib ``DEMA`` / pandas-ta ``dema``.
    """

    spec = IndicatorSpec(
        name="dema",
        category="trend",
        aliases=("Double Exponential MA",),
        inputs=(CLOSE,),
        outputs=("dema",),
        talib_compatible=True,
        references=("Mulloy 1994", "TA-Lib DEMA", "pandas-ta dema"),
        doc="ref/ta_docs/trend/DEMA_TEMA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=1)
        talib_compatible: bool = True

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return dema(df[CLOSE], self.params["length"], self.params["talib_compatible"])
