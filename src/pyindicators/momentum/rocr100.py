"""ROCR100 — Rate of Change Ratio x100: ``100 * close / close_{t-n}`` (momentum)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide


def rocr100(close: pd.Series, length: int = 10) -> pd.Series:
    """Rate of change ratio scaled to 100 (100 = no change)."""
    return 100.0 * safe_divide(close, close.shift(length))


@INDICATORS.register
class ROCR100(Indicator):
    """Rate of Change Ratio (x100).

    What: ROCR scaled by 100 (100.0 = unchanged).
    Best settings: ``length`` 10.
    Edge cases: zero base -> guarded to NaN.
    Parity: TA-Lib ``ROCR100``.
    """

    spec = IndicatorSpec(
        name="rocr100",
        category="momentum",
        aliases=("Rate of Change Ratio 100",),
        inputs=(CLOSE,),
        outputs=("rocr100",),
        talib_compatible=True,
        references=("TA-Lib ROCR100",),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=10, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return rocr100(df[CLOSE], self.params["length"])
