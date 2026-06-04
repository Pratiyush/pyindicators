"""ZLMA — Zero-Lag EMA (Ehlers): ``EMA(close + (close - close_{t-lag}), N)``, lag=(N-1)/2.

Adds the recent momentum back to cancel lag. Composes ``base.ema``.
See ``ref/ta_docs/trend/misc_MA.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def zlma(close: pd.Series, length: int = 10) -> pd.Series:
    """Zero-Lag EMA over ``length`` bars."""
    lag = (length - 1) // 2
    return ema(close + (close - close.shift(lag)), length)


@INDICATORS.register
class ZLMA(Indicator):
    """Zero-Lag Exponential Moving Average.

    What: an EMA with the lag subtracted by adding back recent momentum.
    Best settings: ``length`` 10.
    Edge cases: warm-up = length + lag; inherits EMA seeding.
    Parity: pandas-ta ``zlma`` / finta ``ZLEMA``.
    """

    spec = IndicatorSpec(
        name="zlma",
        category="trend",
        aliases=("Zero-Lag EMA", "ZLEMA"),
        inputs=(CLOSE,),
        outputs=("zlma",),
        references=("Ehlers", "pandas-ta zlma"),
        doc="ref/ta_docs/trend/misc_MA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=10, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return zlma(df[CLOSE], self.params["length"])
