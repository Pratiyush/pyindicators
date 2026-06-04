"""MINMAX — rolling minimum and maximum over a trailing window (math transform).

For each bar, the lowest and highest value of ``close`` across the last ``length`` bars,
returned together as a two-column result. It is exactly the pairing of ``MIN`` and ``MAX``
over the same window — a plain rolling reducer with no smoothing or recurrence — and the
math-transform analogue of TA-Lib ``MINMAX``. Together the two outputs bracket the window
(a Donchian-style channel of ``close``). See ``ref/ta_docs/math_transform/MINMAX.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def minmax(close: pd.Series, length: int = 30) -> dict[str, pd.Series]:
    """Rolling minimum and maximum of ``close`` over a trailing window of ``length`` bars.

    A single trailing window feeds both reducers, so it is causal; ``min_periods=length``
    leaves the first ``length-1`` bars NaN in both outputs (an undersized window has no
    defined extreme). No division is involved, so there is nothing to guard.
    """
    window = close.rolling(length, min_periods=length)
    return {"min": window.min(), "max": window.max()}


@INDICATORS.register
class MinMax(Indicator):
    """Rolling Minimum and Maximum.

    What: the lowest and highest ``close`` over the last ``length`` bars — the support and
    resistance pair that bracket the window (a Donchian-style channel of ``close``).
    Best settings: ``length`` 30 (TA-Lib default); ``max - min`` is the window range.
    Edge cases: first ``length-1`` bars NaN in both columns; a flat window returns the
    constant level for both ``min`` and ``max``.
    Parity: TA-Lib ``MINMAX`` — exact (identical NaN warm-up and bit-for-bit values).
    """

    spec = IndicatorSpec(
        name="minmax",
        category="math_transform",
        aliases=("Rolling Min/Max", "MINMAX"),
        inputs=(CLOSE,),
        outputs=("min", "max"),
        talib_compatible=True,
        references=("TA-Lib MINMAX",),
        doc="ref/ta_docs/math_transform/MINMAX.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        # TA-Lib MINMAX rejects timeperiod < 2 (TA_BAD_PARAM); mirror that lower bound so a
        # window always brackets at least two bars (matching the MININDEX/MAXINDEX siblings).
        length: int = Field(default=30, ge=2)

    def _compute(self, df: pd.DataFrame) -> dict[str, pd.Series]:
        return minmax(df[CLOSE], self.params["length"])
