"""MOM — Momentum: ``close - close_{t-length}`` (momentum)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def mom(close: pd.Series, length: int = 10) -> pd.Series:
    """Absolute momentum: close minus the close ``length`` bars ago."""
    return close.diff(length)


@INDICATORS.register
class MOM(Indicator):
    """Momentum.

    What: the raw price change over ``length`` bars (absolute, not percent).
    Best settings: ``length`` 10.
    Edge cases: first ``length`` bars NaN.
    Parity: TA-Lib ``MOM`` / pandas-ta ``mom``.
    """

    spec = IndicatorSpec(
        name="mom",
        category="momentum",
        aliases=("Momentum",),
        inputs=(CLOSE,),
        outputs=("mom",),
        talib_compatible=True,
        references=("TA-Lib MOM", "pandas-ta mom"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=10, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return mom(df[CLOSE], self.params["length"])
