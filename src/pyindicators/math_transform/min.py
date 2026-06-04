"""MIN — rolling minimum of a series over a trailing window (math transform).

The lowest value of ``close`` across the last ``length`` bars. A plain rolling reducer
(``Series.rolling(length).min()``) with no smoothing or recurrence — the math-transform
analogue of TA-Lib ``MIN``. See ``ref/ta_docs/math_transform/MIN.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def min(close: pd.Series, length: int = 30) -> pd.Series:  # noqa: A001 - registry name "min"
    """Rolling minimum of ``close`` over a trailing window of ``length`` bars.

    A trailing window keeps it causal; ``min_periods=length`` leaves the first
    ``length-1`` bars NaN (an undersized window has no defined minimum).
    """
    return close.rolling(length, min_periods=length).min()


@INDICATORS.register
class MIN(Indicator):
    """Rolling Minimum.

    What: the lowest ``close`` over the last ``length`` bars — a trailing-support line.
    Best settings: ``length`` 30; pair with ``MAX`` for a Donchian-style channel.
    Edge cases: first ``length-1`` bars NaN; a flat window returns that constant level.
    Parity: TA-Lib ``MIN`` (identical warm-up and values for ``length >= 2``).
    """

    spec = IndicatorSpec(
        name="min",
        category="math_transform",
        aliases=("Rolling Minimum", "MIN"),
        inputs=(CLOSE,),
        outputs=("min",),
        talib_compatible=True,
        references=("TA-Lib MIN",),
        doc="ref/ta_docs/math_transform/MIN.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=30, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return min(df[CLOSE], self.params["length"])
