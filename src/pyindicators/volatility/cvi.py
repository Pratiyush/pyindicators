"""Chaikin Volatility (CVI) — rate of change of an EMA of the high-low range.

``CVI = 100 * (EMA(H-L, N) - EMA(H-L, N)_{t-roc}) / EMA(H-L, N)_{t-roc}``. Rising = expanding
volatility. Composes ``base.ema``. See ``ref/ta_docs/volatility/misc_volatility.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec, safe_divide


def cvi(df: pd.DataFrame, length: int = 10, roc_length: int = 10) -> pd.Series:
    """Chaikin Volatility = ROC of EMA(high-low) over ``roc_length`` bars."""
    hl_ema = ema(df[HIGH] - df[LOW], length)
    prev = hl_ema.shift(roc_length)
    return 100.0 * safe_divide(hl_ema - prev, prev)


@INDICATORS.register
class ChaikinVolatility(Indicator):
    """Chaikin Volatility.

    What: percentage change of a smoothed high-low range — expanding vs contracting volatility.
    Best settings: EMA 10, ROC 10.
    Edge cases: zero prior EMA -> guarded; constant range -> 0.
    Parity: standard Chaikin Volatility formula (validated against the explicit definition).
    """

    spec = IndicatorSpec(
        name="cvi",
        category="volatility",
        aliases=("Chaikin Volatility",),
        inputs=(HIGH, LOW),
        outputs=("cvi",),
        references=("Chaikin", "standard CVI"),
        doc="ref/ta_docs/volatility/misc_volatility.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=10, ge=1)
        roc_length: int = Field(default=10, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return cvi(df, self.params["length"], self.params["roc_length"])
