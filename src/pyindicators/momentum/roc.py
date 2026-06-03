"""ROC — Rate of Change (momentum).

Percent change over ``length`` bars: ``ROC = 100 * (close / close_{t-length} - 1)``.
A building block for KST and Coppock. See ``ref/ta_docs/momentum/misc_momentum.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide


def roc(close: pd.Series, length: int = 10) -> pd.Series:
    """Rate of change in percent over ``length`` bars (guarded against a zero base)."""
    prev = close.shift(length)
    return 100.0 * safe_divide(close - prev, prev)


@INDICATORS.register
class ROC(Indicator):
    """Rate of Change.

    What: percentage price change over ``length`` bars — a simple momentum gauge.
    Best settings: 10 (TA-Lib) or 12; longer = slower momentum.
    Edge cases: ``close_{t-length}`` == 0 -> guarded to NaN (degenerate data).
    Parity: TA-Lib ``ROC`` / pandas-ta ``roc``.
    """

    spec = IndicatorSpec(
        name="roc",
        category="momentum",
        aliases=("Rate of Change",),
        inputs=(CLOSE,),
        outputs=("roc",),
        talib_compatible=True,
        references=("TA-Lib ROC", "pandas-ta roc", "tulip roc"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=10, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return roc(df[CLOSE], self.params["length"])
