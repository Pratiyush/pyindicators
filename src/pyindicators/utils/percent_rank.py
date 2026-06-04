"""Percent Rank — rolling percentile of the current close within its recent history (utility).

For each bar, the percent (0-100) of the *prior* ``length`` closes that sit strictly below the
current close::

    percent_rank[i] = 100 * count(close[i-length : i] < close[i]) / length      (i >= length)

The look-back window is the ``length`` bars *before* the current one (``close.shift(1)`` window),
so the result is strictly causal — bar ``i`` reads only rows ``< i`` for the comparison set and
row ``i`` for the value. The denominator is exactly ``length``, which keeps the output cleanly
bounded in ``[0, 100]``:

* a value above its entire recent window -> 100 (a fresh ``length``-bar high),
* a value at or below every prior bar -> 0 (notably a *flat* window: nothing is *strictly*
  below, so a constant series ranks 0, not NaN — there is no division to guard),
* the first ``length`` bars are NaN (insufficient look-back).

This is the ThinkOrSwim / Pine ``percentrank`` family; because it counts *strictly below* over
the prior window (rather than ``<=`` including the current bar), it has a single unambiguous
closed form. No reference library (TA-Lib, pandas-ta(_classic), finta, ``ta``) ships this, so it
is validated against an independent per-window oracle. See ``ref/ta_docs/utils/PercentRank.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def percent_rank(close: pd.Series, length: int = 100) -> pd.Series:
    """Rolling percent rank of ``close`` over the prior ``length`` bars, bounded ``[0, 100]``.

    Returns ``100 * (#prior values strictly below the current close) / length`` per bar, where
    "prior" is the ``length`` bars immediately before the current one. The first ``length`` bars
    are NaN (no full look-back); a flat window yields 0 (nothing strictly below), so the result
    needs no zero-division guard.
    """
    values = close.to_numpy(dtype="float64")
    n = values.size
    out = np.full(n, np.nan, dtype="float64")
    if n > length:
        # win[j] = values[j : j + length]; the prior-window for current bar i (i >= length) is
        # values[i-length : i] == win[i-length]. Drop the final window so it aligns to i=length..n-1.
        windows = sliding_window_view(values, length)[:-1]
        current = values[length:][:, None]
        below = (windows < current).sum(axis=1)
        out[length:] = 100.0 * below / length
    return pd.Series(out, index=close.index)


@INDICATORS.register
class PercentRank(Indicator):
    """Percent Rank.

    What: where the current close sits within its recent history — the percent of the prior
    ``length`` closes that are strictly below it (0 = at/below all of them, 100 = above all).
    Best settings: ``length`` 100 (the default look-back); shorten for a more reactive rank.
    Edge cases: first ``length`` bars NaN; a flat window -> 0 (no value is *strictly* below, so
    there is no division to guard); a fresh window high -> 100.
    Parity: golden-only — no reference library implements this; pinned to an independent
    per-window oracle (see ``tests/parity/test_parity_percent_rank.py``).
    """

    spec = IndicatorSpec(
        name="percent_rank",
        category="utils",
        aliases=("Percent Rank", "Percentile Rank", "PercentRank"),
        inputs=(CLOSE,),
        outputs=("percent_rank",),
        bounds={"percent_rank": (0.0, 100.0)},
        references=("ThinkOrSwim PercentRank", "Pine percentrank"),
        doc="ref/ta_docs/utils/PercentRank.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=100, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return percent_rank(df[CLOSE], self.params["length"])
