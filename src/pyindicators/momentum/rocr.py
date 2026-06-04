"""ROCR — Rate of Change Ratio: ``close / close_{t-n}`` (momentum)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide


def rocr(close: pd.Series, length: int = 10) -> pd.Series:
    """Rate of change as a ratio (close / close n bars ago)."""
    return safe_divide(close, close.shift(length))


@INDICATORS.register
class ROCR(Indicator):
    """Rate of Change Ratio.

    What: price now divided by price ``length`` bars ago (1.0 = no change).
    Best settings: ``length`` 10.
    Edge cases: zero base -> guarded to NaN.
    Parity: TA-Lib ``ROCR``.
    """

    spec = IndicatorSpec(
        name="rocr",
        category="momentum",
        aliases=("Rate of Change Ratio",),
        inputs=(CLOSE,),
        outputs=("rocr",),
        talib_compatible=True,
        references=("TA-Lib ROCR",),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=10, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return rocr(df[CLOSE], self.params["length"])
