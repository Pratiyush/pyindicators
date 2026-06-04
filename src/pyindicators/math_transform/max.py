"""MAX — rolling maximum of a series over a trailing window (math transform).

The highest value of ``close`` across the last ``length`` bars. A plain rolling reducer
(``Series.rolling(length).max()``) with no smoothing or recurrence — the math-transform
analogue of TA-Lib ``MAX``. See ``ref/ta_docs/math_transform/MAX.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def max(close: pd.Series, length: int = 30) -> pd.Series:  # noqa: A001 - registry name "max"
    """Rolling maximum of ``close`` over a trailing window of ``length`` bars.

    A trailing window keeps it causal; ``min_periods=length`` leaves the first
    ``length-1`` bars NaN (an undersized window has no defined maximum).
    """
    return close.rolling(length, min_periods=length).max()


@INDICATORS.register
class MAX(Indicator):
    """Rolling Maximum.

    What: the highest ``close`` over the last ``length`` bars — a trailing-resistance line.
    Best settings: ``length`` 30; pair with ``MIN`` for a Donchian-style channel.
    Edge cases: first ``length-1`` bars NaN; a flat window returns that constant level.
    Parity: TA-Lib ``MAX`` (identical warm-up and values for ``length >= 2``).
    """

    spec = IndicatorSpec(
        name="max",
        category="math_transform",
        aliases=("Rolling Maximum", "MAX"),
        inputs=(CLOSE,),
        outputs=("max",),
        talib_compatible=True,
        references=("TA-Lib MAX",),
        doc="ref/ta_docs/math_transform/MAX.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=30, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return max(df[CLOSE], self.params["length"])
