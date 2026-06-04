"""CDLMATCHINGLOW — Matching Low pattern (two bars, bullish only).

Two consecutive **black** (down) candles whose **closes match** — the second candle closes at
(approximately) the same level as the first, forming a support/"matching low". TA-Lib::

    color(prev) == -1                                 # first candle is black
    AND color(cur)  == -1                             # second candle is black
    AND close(cur) <= close(prev) + Equal average(prev)
    AND close(cur) >= close(prev) - Equal average(prev)   # the two closes are ~equal

The pattern is **bullish only**: the output is a pure ``100`` / ``0`` signal (TA-Lib never emits a
negative value or an ±80 partial-penetration score here — the "close equality" is itself a
tolerance band via the ``Equal`` setting, not a strict edge tie).

``Equal`` is ``(HighLow, 5, 0.05)``. The previous bar's ``Equal`` average needs 5 earlier bars,
so TA-Lib's lookback is ``5 + 1 = 6`` (the first 6 bars are forced to 0). This was verified
boundary-exact against ``talib.CDLMATCHINGLOW`` (first possible signal at bar index 6).
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color

# TA-Lib reports a lookback of 6 for CDLMATCHINGLOW: Equal avgPeriod (5) + 1, the +1 coming from
# the previous-bar Equal average (which itself consumes 5 prior bars). Confirmed boundary-exact.
_LOOKBACK = 6


def matching_low(df: pd.DataFrame) -> pd.Series:
    """Matching Low pattern over ``df`` (OHLC) as a 0/100 ``Series``.

    Matches ``talib.CDLMATCHINGLOW`` bit-exactly: two consecutive black candles whose closes
    coincide (within the ``Equal`` average of the first bar) yield ``100``, else ``0``. The first
    6 bars are 0 (TA-Lib lookback). Output is pure 0/100 — bullish only, no negative or ±80 score.
    """
    c = df[CLOSE].to_numpy(dtype="float64")
    equal = candle_average(df, "Equal").to_numpy()
    color = candle_color(df).to_numpy()
    n = len(c)
    out = np.zeros(n, dtype="float64")

    # Previous = bars [0..n-2], current = bars [1..n-1]; color == -1 is a black candle (close<open).
    prev_black = color[:-1] == -1
    cur_black = color[1:] == -1
    # NaN Equal average during warm-up -> comparisons are False -> 0 (then also forced by lookback).
    close_meets = (c[1:] <= c[:-1] + equal[:-1]) & (c[1:] >= c[:-1] - equal[:-1])

    hit = prev_black & cur_black & close_meets
    out[1:] = np.where(hit, 100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 6 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class MatchingLow(Indicator):
    """Matching Low candlestick pattern.

    What: two consecutive black candles closing at the same level — a potential support/reversal.
    Best settings: parameterless; both candles must be black and their closes ~equal (within the
    ``Equal`` tolerance band of the first candle's range).
    Edge cases: bullish-only pure 0/100 (no negative, no ±80 partial score); first 6 bars are 0.
    Parity: TA-Lib ``CDLMATCHINGLOW`` (Equal = HighLow/5/0.05), exact integer match.
    """

    class Params(BaseModel):
        """Parameters for Matching Low (TA-Lib ``CDLMATCHINGLOW`` takes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="matching_low",
        category="candles",
        aliases=("MatchingLow", "CDLMATCHINGLOW"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("matching_low",),
        bounds={"matching_low": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLMATCHINGLOW",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return matching_low(df)
