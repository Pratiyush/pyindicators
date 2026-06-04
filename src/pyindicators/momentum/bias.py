"""Bias — percentage deviation of price from its moving average (``close/SMA - 1``)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide


def bias(close: pd.Series, length: int = 26) -> pd.Series:
    """Bias = close / SMA(close, length) - 1 (fractional deviation)."""
    m = sma(close, length)
    return safe_divide(close - m, m)


@INDICATORS.register
class Bias(Indicator):
    """Bias.

    What: how far price sits above/below its SMA, as a fraction.
    Best settings: ``length`` 26; large |bias| = stretched (mean-reversion candidate).
    Edge cases: SMA 0 -> guarded (prices are positive in practice).
    Parity: pandas-ta ``bias``.
    """

    spec = IndicatorSpec(
        name="bias",
        category="momentum",
        aliases=("Bias",),
        inputs=(CLOSE,),
        outputs=("bias",),
        references=("pandas-ta bias",),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=26, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return bias(df[CLOSE], self.params["length"])
