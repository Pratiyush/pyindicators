"""CDLBELTHOLD — Belt-hold candlestick (single bar, directional, magnitude 100).

A belt-hold is a long-bodied candle whose *opening* end has no (or negligible) shadow: the
open sits at the extreme of the bar (it is an "opening marubozu"). For a white candle the open
is the low, so the **lower** shadow must vanish; for a black candle the open is the high, so
the **upper** shadow must vanish. The opposite (closing) shadow is unconstrained — that is the
mirror image of the Closing Marubozu, which constrains the closing side instead. TA-Lib::

    RealBody > BodyLong average                                   # long body
    AND ( (white AND lower_shadow < ShadowVeryShort average)      # open at the bottom
          OR (black AND upper_shadow < ShadowVeryShort average) ) # open at the top

``BodyLong`` is ``(RealBody, 10, 1.0)`` and ``ShadowVeryShort`` is ``(HighLow, 10, 0.1)``.
Output is +100 for a white (bullish) belt-hold, -100 for a black (bearish) one, else 0. There
is no partial-penetration (±80) score: the shadow test is a strict inequality against an
average, so a body edge never merely "ties" (verified — only -100/0/100 appear). TA-Lib takes
no ``penetration`` parameter for this pattern. Its lookback is 10 (the BodyLong period); the
first 10 bars are forced to 0.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, lower_shadow, real_body, upper_shadow

# TA-Lib reports a lookback of 10 for CDLBELTHOLD (BodyLong period 10).
_LOOKBACK = 10


def belt_hold(df: pd.DataFrame) -> pd.Series:
    """Belt-hold pattern over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDLBELTHOLD`` bit-exactly: a long body whose opening end has a very short
    shadow (white -> short lower, black -> short upper); sign is the candle colour (+1 white /
    -1 black). The first 10 bars are 0 (TA-Lib lookback).
    """
    rb = real_body(df)
    body_long = candle_average(df, "BodyLong")
    very_short = candle_average(df, "ShadowVeryShort")
    color = candle_color(df).to_numpy()

    long_body = rb > body_long  # NaN average during warm-up -> False
    white_opened = (color == 1) & (lower_shadow(df) < very_short)
    black_opened = (color == -1) & (upper_shadow(df) < very_short)
    hit = long_body & (white_opened | black_opened)

    out = np.where(hit, color * 100.0, 0.0)
    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 10 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class BeltHold(Indicator):
    """Belt-hold candlestick.

    What: a long body whose *opening* end has no shadow (open at the bar extreme) — strong
    conviction from the open, with the closing side free to have a shadow.
    Best settings: parameterless; body > 10-bar average body, opening shadow < 10% of the
    average range.
    Edge cases: first 10 bars are 0; +100 white (bullish) / -100 black (bearish); only the
    opening-side shadow is constrained (the closing-side shadow may be long). No ±80 score.
    Parity: TA-Lib ``CDLBELTHOLD`` (BodyLong = RealBody/10/1.0, ShadowVeryShort =
    HighLow/10/0.1), exact integer match.
    """

    spec = IndicatorSpec(
        name="belt_hold",
        category="candles",
        aliases=("Belt Hold", "CDLBELTHOLD"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("belt_hold",),
        bounds={"belt_hold": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLBELTHOLD",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return belt_hold(df)
