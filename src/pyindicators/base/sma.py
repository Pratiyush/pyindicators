"""SMA — Simple Moving Average (base / overlap primitive).

The unweighted mean of the last ``length`` values; the building block for Bollinger,
TRIMA, Stochastic %D, CMF windows, KST, and more. First ``length-1`` outputs are NaN.
See the 10-section spec at ``ref/ta_docs/base/SMA.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def sma(series: pd.Series, length: int) -> pd.Series:
    """Simple moving average: trailing mean over ``length`` bars (``min_periods == length``)."""
    return series.rolling(length, min_periods=length).mean()


@INDICATORS.register
class SMA(Indicator):
    """Simple Moving Average.

    What: the equal-weight mean of the last ``length`` closes — the most basic smoother.
    Best settings: ``length`` 10/20/50/100/200; 50/200 crossovers are the golden/death cross.
    Edge cases: first ``length-1`` bars are NaN (warm-up); a NaN inside the window propagates.
    Parity: exact vs TA-Lib ``SMA`` / pandas-ta ``sma``.
    """

    spec = IndicatorSpec(
        name="sma",
        category="base",
        aliases=("Moving Average", "MA", "Arithmetic MA"),
        inputs=(CLOSE,),
        outputs=("sma",),
        talib_compatible=True,
        references=("TA-Lib SMA", "pandas-ta sma", "tulip sma"),
        doc="ref/ta_docs/base/SMA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return sma(df[CLOSE], self.params["length"])
