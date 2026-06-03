"""ATR — Average True Range (volatility, Wilder 1978).

Wilder-smoothed average of True Range: a pure (directionless) volatility measure and the
base for Supertrend, Keltner, Chandelier, and ATR position-sizing. Composes
``base.true_range`` + ``base.rma`` (first ATR = simple mean of the first N true ranges).
See ``ref/ta_docs/volatility/ATR_NATR.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import rma, true_range
from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def atr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    """Average True Range = Wilder-RMA of True Range over ``length`` bars."""
    return rma(true_range(df), length)


@INDICATORS.register
class ATR(Indicator):
    """Average True Range.

    What: the Wilder-smoothed mean bar movement (gap-aware); volatility, not direction.
    Best settings: ``length`` 14 (Wilder); used for stops (2-3x ATR) and position sizing.
    Edge cases: first TR = H-L; flat market -> ATR 0.
    Parity: pandas-ta ``atr`` (RMA, first TR = H-L). TA-Lib seeds from bar 1 (converges later).
    """

    spec = IndicatorSpec(
        name="atr",
        category="volatility",
        aliases=("Average True Range",),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("atr",),
        talib_compatible=True,
        references=("Wilder 1978", "TA-Lib ATR", "pandas-ta atr"),
        doc="ref/ta_docs/volatility/ATR_NATR.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return atr(df, self.params["length"])
