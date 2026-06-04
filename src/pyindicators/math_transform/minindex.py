"""MININDEX — absolute bar index of the rolling minimum (math transform).

For each bar, the *integer position* (absolute bar index) of the lowest ``close`` across the
last ``length`` bars — TA-Lib ``MININDEX`` (the "where is the low" companion of ``MIN``).
A trailing-window reducer; the only subtlety is tie-breaking, which follows TA-Lib's
incremental scan exactly (see below). See ``ref/ta_docs/math_transform/MININDEX.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def minindex(close: pd.Series, length: int = 30) -> pd.Series:
    """Absolute bar index of the rolling minimum of ``close`` over ``length`` bars.

    Returns, for each bar ``i`` (``i >= length-1``), the absolute index ``j`` (``0``-based,
    ``i-length+1 <= j <= i``) of the smallest value in the trailing window; the first
    ``length-1`` bars are NaN (an undersized window has no defined argmin).

    Tie-breaking matches TA-Lib's *stateful* scan rather than ``numpy.argmin``: the running
    low index is only re-derived (preferring the **earliest** equal low) when the current low
    rolls out of the window; on every other bar a new value merely ``<=`` the running low
    adopts the **latest** index. ``np.argmin`` (always-earliest) would diverge on ties.
    """
    values = close.to_numpy(dtype="float64")
    n = values.shape[0]
    out = np.full(n, np.nan, dtype="float64")
    lookback = length - 1
    if n <= lookback:
        return pd.Series(out, index=close.index)

    trailing_idx = 0  # oldest bar still inside the current window
    lowest_idx = -1  # absolute index of the running minimum (-1 forces an initial rescan)
    lowest = 0.0
    for today in range(lookback, n):
        value = values[today]
        if lowest_idx < trailing_idx:
            # The previous low has aged out of the window -> rescan it; strict ``<`` keeps the
            # EARLIEST of any equal lows.
            lowest_idx = trailing_idx
            lowest = values[lowest_idx]
            for scan in range(trailing_idx + 1, today + 1):
                candidate = values[scan]
                if candidate < lowest:
                    lowest_idx = scan
                    lowest = candidate
        elif value <= lowest:
            # Incremental step: ``<=`` lets the LATEST bar win ties with the running low.
            lowest_idx = today
            lowest = value
        out[today] = float(lowest_idx)
        trailing_idx += 1
    return pd.Series(out, index=close.index)


@INDICATORS.register
class MinIndex(Indicator):
    """Min Index (absolute index of the rolling minimum).

    What: the absolute bar index of the lowest ``close`` over the last ``length`` bars.
    Best settings: ``length`` 30; pair with ``MAXINDEX`` to time channel touches / bar-age.
    Edge cases: first ``length-1`` bars NaN; ties resolve per TA-Lib's incremental scan
    (latest index on an incremental update, earliest on a re-scan), not ``np.argmin``.
    Parity: TA-Lib ``MININDEX`` (exact integer match on the valid region; ``length >= 2``).
    """

    spec = IndicatorSpec(
        name="minindex",
        category="math_transform",
        aliases=("MININDEX", "Index of Minimum"),
        inputs=(CLOSE,),
        outputs=("minindex",),
        talib_compatible=True,
        references=("TA-Lib MININDEX",),
        doc="ref/ta_docs/math_transform/MININDEX.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=30, ge=2)  # TA-Lib MININDEX rejects timeperiod < 2

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return minindex(df[CLOSE], self.params["length"])
