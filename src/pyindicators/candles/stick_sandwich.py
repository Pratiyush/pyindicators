"""CDLSTICKSANDWICH — Stick Sandwich pattern (three bars, bullish only).

A black candle is "sandwiched" between two others such that the third candle closes back at
(approximately) the same level as the first, trapping a white candle in between. TA-Lib::

    color(1st) == -1                                   # 1st candle is black
    AND color(2nd) == 1                                # 2nd candle is white
    AND color(3rd) == -1                               # 3rd candle is black
    AND low(2nd)  > close(1st)                          # 2nd trades entirely above the 1st close
    AND close(3rd) <= close(1st) + Equal average(1st)   # 3rd closes ~equal to the 1st close
    AND close(3rd) >= close(1st) - Equal average(1st)

The pattern is **bullish only**: the output is a pure ``100`` / ``0`` signal (TA-Lib never emits a
negative value or an ±80 partial-penetration score here — the "close equality" is itself a
tolerance band via the ``Equal`` setting, not a strict edge tie). There is no penetration
parameter (``talib.CDLSTICKSANDWICH`` takes none).

``Equal`` is ``(HighLow, 5, 0.05)`` and its average is evaluated at the **first** candle of the
triple (index ``i-2``), i.e. over the 5 bars ending at ``i-3``. That average needs 5 bars before
the first candle, so TA-Lib's lookback is ``5 + 2 = 7`` (the first 7 bars are forced to 0).
Verified boundary-exact against ``talib.CDLSTICKSANDWICH`` (first possible signal at bar 7).
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color

# TA-Lib reports a lookback of 7 for CDLSTICKSANDWICH: Equal avgPeriod (5) + 2, the +2 coming
# from the two prior bars of the three-candle pattern. Confirmed boundary-exact.
_LOOKBACK = 7


def stick_sandwich(df: pd.DataFrame) -> pd.Series:
    """Stick Sandwich pattern over ``df`` (OHLC) as a 0/100 ``Series``.

    Matches ``talib.CDLSTICKSANDWICH`` bit-exactly: ``100`` where a black / white / black triple
    has the white candle's low strictly above the first close and the third close coinciding
    with the first close (within the first bar's ``Equal`` average), else ``0``. The first 7 bars
    are 0 (TA-Lib lookback). Output is pure 0/100 — bullish only, no negative or ±80 score.
    """
    c = df[CLOSE].to_numpy(dtype="float64")
    low = df[LOW].to_numpy(dtype="float64")
    equal = candle_average(df, "Equal").to_numpy()
    color = candle_color(df).to_numpy()
    n = len(c)
    out = np.zeros(n, dtype="float64")

    # 1st = bars [0..n-3], 2nd = bars [1..n-2], 3rd (current) = bars [2..n-1].
    first_black = color[:-2] == -1
    second_white = color[1:-1] == 1
    third_black = color[2:] == -1
    # 2nd candle's low strictly above the 1st close (strict, verified).
    second_above = low[1:-1] > c[:-2]
    # 3rd close within the 1st bar's Equal band (non-strict both edges, verified).
    # NaN Equal average during warm-up -> comparisons are False -> 0 (then also forced by lookback).
    close_meets = (c[2:] <= c[:-2] + equal[:-2]) & (c[2:] >= c[:-2] - equal[:-2])

    hit = first_black & second_white & third_black & second_above & close_meets
    out[2:] = np.where(hit, 100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 7 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class StickSandwich(Indicator):
    """Stick Sandwich candlestick pattern.

    What: a white candle trapped between two black candles whose closes coincide — a potential
    bullish reversal at support.
    Best settings: parameterless; all three candle colours must match (black/white/black), the
    middle low must clear the first close, and the third close must return to the first close.
    Edge cases: bullish-only pure 0/100 (no negative, no ±80 partial score); first 7 bars are 0.
    Parity: TA-Lib ``CDLSTICKSANDWICH`` (Equal = HighLow/5/0.05), exact integer match.
    """

    class Params(BaseModel):
        """Parameters for Stick Sandwich (TA-Lib ``CDLSTICKSANDWICH`` takes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="stick_sandwich",
        category="candles",
        aliases=("StickSandwich", "CDLSTICKSANDWICH"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("stick_sandwich",),
        bounds={"stick_sandwich": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLSTICKSANDWICH",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return stick_sandwich(df)
