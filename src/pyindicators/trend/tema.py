"""TEMA — Triple Exponential Moving Average (low-lag, Patrick Mulloy 1994).

``TEMA = 3*e1 - 3*e2 + e3`` where e1=EMA(price), e2=EMA(e1), e3=EMA(e2). Composes
``base.ema``. See ``ref/ta_docs/trend/DEMA_TEMA.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def tema(close: pd.Series, length: int = 20, talib_compatible: bool = True) -> pd.Series:
    """Triple EMA = 3*e1 - 3*e2 + e3 (nested EMAs)."""
    e1 = ema(close, length, talib_compatible)
    e2 = ema(e1, length, talib_compatible)
    e3 = ema(e2, length, talib_compatible)
    return 3.0 * e1 - 3.0 * e2 + e3


@INDICATORS.register
class TEMA(Indicator):
    """Triple Exponential Moving Average.

    What: an even-lower-lag smoother than DEMA, from triple-nested EMAs.
    Best settings: ``length`` 20; smaller for faster signals.
    Edge cases: long warm-up (~3*length); inherits the EMA seeding convention.
    Parity: TA-Lib ``TEMA`` / pandas-ta ``tema``.
    """

    spec = IndicatorSpec(
        name="tema",
        category="trend",
        aliases=("Triple Exponential MA",),
        inputs=(CLOSE,),
        outputs=("tema",),
        talib_compatible=True,
        references=("Mulloy 1994", "TA-Lib TEMA", "pandas-ta tema"),
        doc="ref/ta_docs/trend/DEMA_TEMA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=1)
        talib_compatible: bool = True

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return tema(df[CLOSE], self.params["length"], self.params["talib_compatible"])
