"""MAXINDEX — absolute index of the rolling maximum over a trailing window (math transform).

For each bar, the position (absolute index into the input series) of the highest ``close``
across the last ``length`` bars. This is the index-returning sibling of ``MAX`` and the
math-transform analogue of TA-Lib ``MAXINDEX``. A pure rolling reducer with no smoothing or
recurrence. See ``ref/ta_docs/math_transform/MAXINDEX.md``.

What: where (not what) the window maximum sits — useful for "bars since the high" / recency
of strength signals; ``i - maxindex`` is the age of the current window high.
Best settings: ``length`` 30 (TA-Lib default); pair with ``MININDEX`` to bracket a window.
Edge cases: first ``length-1`` bars are the fill value 0 (undersized window, matching
TA-Lib's lookback fill); a flat window resolves to the *earliest* bar in that window.
Parity: TA-Lib ``MAXINDEX`` — exact, including its tie-break convention (see ``_maxindex``).

Tie-break (faithful to TA-Lib ta_MAXINDEX.c): the running maximum is carried forward; when a
new bar ties the carried maximum it *takes over* (newest wins, ``>=``), but when the previous
maximum scrolls out of the window and the whole window is rescanned forward, the *earliest*
maximum is kept (``>`` strict). Plain ``argmax`` (first-in-window) does NOT reproduce this, so
the indicator is computed with an explicit O(n) scan rather than ``rolling().apply(argmax)``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def _maxindex(values: np.ndarray, length: int) -> np.ndarray:
    """Absolute index of the trailing-window maximum, replicating TA-Lib ta_MAXINDEX.c.

    Single forward pass: ``highest_idx`` is reused across bars while it stays inside the
    window (incremental ``>=`` so the newest bar wins ties); once it scrolls out, the window
    ``[trailing_idx, today]`` is rescanned with strict ``>`` so the *earliest* maximum is
    retained. The first ``length-1`` outputs keep the fill value 0.
    """
    n = values.size
    out = np.zeros(n, dtype="float64")  # lookback fill (TA-Lib emits 0 here)
    lookback = length - 1
    if lookback >= n:
        return out
    today = lookback
    trailing_idx = 0
    highest_idx = -1
    highest = 0.0
    while today < n:
        cur = values[today]
        if highest_idx < trailing_idx:
            # Previous maximum has left the window: rescan [trailing_idx, today].
            highest_idx = trailing_idx
            highest = values[highest_idx]
            i = highest_idx
            while i < today:
                i += 1
                v = values[i]
                if v > highest:  # strict: earliest maximum wins on a tie
                    highest_idx = i
                    highest = v
        elif cur >= highest:  # incremental: newest bar wins on a tie
            highest_idx = today
            highest = cur
        out[today] = highest_idx
        trailing_idx += 1
        today += 1
    return out


def maxindex(close: pd.Series, length: int = 30) -> pd.Series:
    """Absolute index of the rolling maximum of ``close`` over ``length`` trailing bars.

    Trailing-only, so causal; the first ``length-1`` bars are 0 (TA-Lib's lookback fill,
    not a true index). Returned as float64 to honour the library's uniform output contract.
    """
    values = close.to_numpy(dtype="float64")
    return pd.Series(_maxindex(values, length), index=close.index)


@INDICATORS.register
class MaxIndex(Indicator):
    """Index of Rolling Maximum.

    What: the absolute position of the highest ``close`` over the last ``length`` bars.
    Best settings: ``length`` 30 (TA-Lib); ``i - maxindex`` gives "bars since the high".
    Edge cases: first ``length-1`` bars are the fill 0; a flat window -> earliest bar.
    Parity: TA-Lib ``MAXINDEX`` (exact values and tie-break; warm-up filled with 0).
    """

    spec = IndicatorSpec(
        name="maxindex",
        category="math_transform",
        aliases=("Index of Highest Value", "MAXINDEX"),
        inputs=(CLOSE,),
        outputs=("maxindex",),
        talib_compatible=True,
        references=("TA-Lib MAXINDEX",),
        doc="ref/ta_docs/math_transform/MAXINDEX.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=30, ge=2)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return maxindex(df[CLOSE], self.params["length"])
