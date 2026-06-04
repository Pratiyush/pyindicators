"""MINMAXINDEX — absolute bar indices of the rolling minimum AND maximum (math transform).

For each bar, the *integer positions* (absolute, ``0``-based indices into ``close``) of both the
lowest and the highest value across the last ``length`` bars — TA-Lib ``MINMAXINDEX``, the
two-output companion of ``MINMAX`` and the fused twin of ``MININDEX`` + ``MAXINDEX``. It returns
``minidx`` and ``maxidx``: where the window low and window high sit, so ``i - minidx`` /
``i - maxidx`` give the bar-age of each extreme. A pure trailing-window reducer (no smoothing,
no recurrence), so causal; the only subtlety is tie-breaking, which follows TA-Lib's stateful
incremental scan exactly (see below). See ``ref/ta_docs/math_transform/MINMAXINDEX.md``.

No division is involved, so no ``safe_divide`` guard is needed; the outputs are plain integer
positions emitted as float64 to honour the library's uniform output contract.

Tie-break (faithful to TA-Lib ta_MINMAXINDEX.c, which is MININDEX and MAXINDEX run in lockstep):
each running extreme index is carried forward while it stays inside the window and is overtaken
by a newer *equal* bar (incremental ``<=`` for the low, ``>=`` for the high — newest wins); once
it scrolls out of the window the whole window ``[trailing_idx, today]`` is rescanned with a
*strict* comparison (``<`` / ``>``), keeping the *earliest* equal extreme. Plain ``np.argmin`` /
``np.argmax`` (always-earliest) do NOT reproduce the incremental case, so each extreme is tracked
with an explicit O(n) forward pass rather than ``rolling().apply(argmin/argmax)``.

Warm-up: TA-Lib back-fills the first ``length-1`` bars of BOTH outputs with ``0`` (its lookback
fill, not a real index). We reproduce that 0-fill exactly so parity holds over the full series
(this differs from the sibling ``MININDEX`` which leaves its warm-up NaN).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def _minmaxindex(values: np.ndarray, length: int) -> tuple[np.ndarray, np.ndarray]:
    """Absolute indices of the trailing-window min and max, replicating ta_MINMAXINDEX.c.

    Single forward pass tracking ``lowest_idx`` and ``highest_idx`` together: each is reused
    across bars while it remains inside the window (incremental ``<=`` / ``>=`` so the newest bar
    wins ties); once it scrolls out, the window ``[trailing_idx, today]`` is rescanned with strict
    ``<`` / ``>`` so the *earliest* extreme is retained. The first ``length-1`` outputs keep the
    fill value 0 (TA-Lib's lookback fill).
    """
    n = values.size
    min_out = np.zeros(n, dtype="float64")  # lookback fill (TA-Lib emits 0 here)
    max_out = np.zeros(n, dtype="float64")
    lookback = length - 1
    if lookback >= n:
        return min_out, max_out

    trailing_idx = 0  # oldest bar still inside the current window
    lowest_idx = -1  # -1 forces an initial rescan
    highest_idx = -1
    lowest = 0.0
    highest = 0.0
    for today in range(lookback, n):
        cur = values[today]
        # --- rolling minimum ----------------------------------------------------------
        if lowest_idx < trailing_idx:
            # Previous low has aged out of the window -> rescan; strict ``<`` keeps the EARLIEST.
            lowest_idx = trailing_idx
            lowest = values[lowest_idx]
            for scan in range(trailing_idx + 1, today + 1):
                candidate = values[scan]
                if candidate < lowest:
                    lowest_idx = scan
                    lowest = candidate
        elif cur <= lowest:
            # Incremental step: ``<=`` lets the LATEST bar win ties with the running low.
            lowest_idx = today
            lowest = cur
        # --- rolling maximum ----------------------------------------------------------
        if highest_idx < trailing_idx:
            # Previous high has aged out -> rescan; strict ``>`` keeps the EARLIEST.
            highest_idx = trailing_idx
            highest = values[highest_idx]
            for scan in range(trailing_idx + 1, today + 1):
                candidate = values[scan]
                if candidate > highest:
                    highest_idx = scan
                    highest = candidate
        elif cur >= highest:
            # Incremental step: ``>=`` lets the LATEST bar win ties with the running high.
            highest_idx = today
            highest = cur
        min_out[today] = lowest_idx
        max_out[today] = highest_idx
        trailing_idx += 1
    return min_out, max_out


def minmaxindex(close: pd.Series, length: int = 30) -> dict[str, pd.Series]:
    """Absolute indices of the rolling min and max of ``close`` over ``length`` trailing bars.

    Returns ``{"minidx", "maxidx"}``, each the absolute ``0``-based position of the lowest /
    highest value in the trailing window ``[i-length+1, i]``. Trailing-only, so causal; the first
    ``length-1`` bars are the fill 0 (TA-Lib's lookback fill, not a real index). Emitted as
    float64 to honour the library's uniform output contract.
    """
    values = close.to_numpy(dtype="float64")
    min_out, max_out = _minmaxindex(values, length)
    return {
        "minidx": pd.Series(min_out, index=close.index),
        "maxidx": pd.Series(max_out, index=close.index),
    }


@INDICATORS.register
class MinMaxIndex(Indicator):
    """Min/Max Index (absolute indices of the rolling minimum and maximum).

    What: the absolute bar positions of the lowest and highest ``close`` over the last ``length``
    bars (``minidx``, ``maxidx``); ``i - minidx`` / ``i - maxidx`` give "bars since the low/high".
    Best settings: ``length`` 30 (TA-Lib default); the fused alternative to running ``MININDEX``
    and ``MAXINDEX`` separately.
    Edge cases: first ``length-1`` bars are the fill 0; ties resolve per TA-Lib's incremental scan
    (latest index on an incremental update, earliest on a re-scan), not ``np.argmin``/``argmax``.
    Parity: TA-Lib ``MINMAXINDEX`` — exact integer match on both outputs, including warm-up 0-fill
    and tie-break (``length >= 2``).
    """

    spec = IndicatorSpec(
        name="minmaxindex",
        category="math_transform",
        aliases=("MINMAXINDEX", "Indices of Lowest and Highest Values"),
        inputs=(CLOSE,),
        outputs=("minidx", "maxidx"),
        talib_compatible=True,
        references=("TA-Lib MINMAXINDEX",),
        doc="ref/ta_docs/math_transform/MINMAXINDEX.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=30, ge=2)  # TA-Lib MINMAXINDEX rejects timeperiod < 2

    def _compute(self, df: pd.DataFrame) -> dict[str, pd.Series]:
        return minmaxindex(df[CLOSE], self.params["length"])
