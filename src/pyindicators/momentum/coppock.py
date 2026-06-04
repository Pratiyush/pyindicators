"""Coppock Curve — long-term momentum bottoming signal (Edwin Coppock).

``Coppock = WMA( ROC(long) + ROC(short), wma_length )``. Composes ``momentum.roc`` +
``base.wma``. See ``ref/ta_docs/momentum/misc_momentum.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import wma
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec
from pyindicators.momentum.roc import roc


def coppock(close: pd.Series, long: int = 14, short: int = 11, length: int = 10) -> pd.Series:
    """Coppock Curve = WMA(ROC(long) + ROC(short), length)."""
    return wma(roc(close, long) + roc(close, short), length)


@INDICATORS.register
class Coppock(Indicator):
    """Coppock Curve.

    What: a smoothed sum of two ROCs — a long-term (monthly) bottoming signal.
    Best settings: ROC 14 & 11, WMA 10 (Coppock); zero-line upturn = buy.
    Edge cases: long warm-up (longest ROC + WMA).
    Parity: pandas-ta ``coppock`` (not in core TA-Lib).
    """

    spec = IndicatorSpec(
        name="coppock",
        category="momentum",
        aliases=("Coppock Curve",),
        inputs=(CLOSE,),
        outputs=("coppock",),
        references=("Coppock", "pandas-ta coppock"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        long: int = Field(default=14, ge=1)
        short: int = Field(default=11, ge=1)
        length: int = Field(default=10, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        p = self.params
        return coppock(df[CLOSE], p["long"], p["short"], p["length"])
