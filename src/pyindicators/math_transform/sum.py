"""SUM — rolling sum of a series over a trailing window (math transform).

The running total of ``close`` across the last ``length`` bars. A plain rolling reducer
(``Series.rolling(length).sum()``) with no smoothing or recurrence — the math-transform
analogue of TA-Lib ``SUM`` (and the unscaled core of ``SMA``, which is this divided by
``length``). See ``ref/ta_docs/math_transform/SUM.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def sum(close: pd.Series, length: int = 30) -> pd.Series:  # noqa: A001 - registry name "sum"
    """Rolling sum of ``close`` over a trailing window of ``length`` bars.

    A trailing window keeps it causal; ``min_periods=length`` leaves the first
    ``length-1`` bars NaN (an undersized window has no defined total, matching TA-Lib's
    warm-up rather than fabricating a partial sum).
    """
    return close.rolling(length, min_periods=length).sum()


@INDICATORS.register
class SUM(Indicator):
    """Rolling Sum.

    What: the running total of ``close`` over the last ``length`` bars — the unscaled
    basis of the SMA (``SMA == SUM / length``).
    Best settings: ``length`` 30; any window where an accumulated total (not an average)
    is wanted, e.g. summing a volume or one-bar-change series.
    Edge cases: first ``length-1`` bars NaN; a flat window returns ``length * level``;
    ``length`` 1 is a passthrough of ``close``.
    Parity: TA-Lib ``SUM`` (identical warm-up and bit-for-bit values for ``length >= 2``;
    TA-Lib rejects ``timeperiod`` 1, which we still support as a plain passthrough).
    """

    spec = IndicatorSpec(
        name="sum",
        category="math_transform",
        aliases=("Rolling Sum", "SUM"),
        inputs=(CLOSE,),
        outputs=("sum",),
        talib_compatible=True,
        references=("TA-Lib SUM",),
        doc="ref/ta_docs/math_transform/SUM.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=30, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return sum(df[CLOSE], self.params["length"])
