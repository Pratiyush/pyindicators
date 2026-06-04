"""CDLCLOSINGMARUBOZU — Closing Marubozu candlestick (single bar, directional, magnitude 100).

A closing marubozu is a long-bodied candle whose *closing* end has no (or negligible) shadow:
the close sits at the extreme of the bar. For a white candle the close is the high, so the
**upper** shadow must vanish; for a black candle the close is the low, so the **lower** shadow
must vanish. The opposite (opening) shadow is unconstrained — that is the only difference from
the plain Marubozu. TA-Lib's test::

    RealBody > BodyLong average                                   # long body
    AND ( (white AND upper_shadow < ShadowVeryShort average)      # close at the top
          OR (black AND lower_shadow < ShadowVeryShort average) ) # close at the bottom

``BodyLong`` is ``(RealBody, 10, 1.0)`` and ``ShadowVeryShort`` is ``(HighLow, 10, 0.1)``.
Output is +100 for a white closing marubozu, -100 for a black one, else 0. There is no
partial-penetration (±80) score: the shadow test is a strict inequality against an average,
so a body edge never merely "ties". TA-Lib's lookback is 10 (the BodyLong period); the first
10 bars are forced to 0.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, lower_shadow, real_body, upper_shadow

# TA-Lib reports a lookback of 10 for CDLCLOSINGMARUBOZU (BodyLong period 10).
_LOOKBACK = 10


def closing_marubozu(df: pd.DataFrame) -> pd.Series:
    """Closing Marubozu pattern over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDLCLOSINGMARUBOZU`` bit-exactly: a long body whose closing end has a
    very short shadow (white -> short upper, black -> short lower); sign is the candle colour
    (+1 white / -1 black). The first 10 bars are 0 (TA-Lib lookback).
    """
    rb = real_body(df)
    body_long = candle_average(df, "BodyLong")
    very_short = candle_average(df, "ShadowVeryShort")
    color = candle_color(df).to_numpy()

    long_body = rb > body_long  # NaN average during warm-up -> False
    white_closed = (color == 1) & (upper_shadow(df) < very_short)
    black_closed = (color == -1) & (lower_shadow(df) < very_short)
    hit = long_body & (white_closed | black_closed)

    out = np.where(hit, color * 100.0, 0.0)
    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 10 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class ClosingMarubozu(Indicator):
    """Closing Marubozu candlestick.

    What: a long body whose *closing* end has no shadow (close at the bar extreme) — strong
    conviction into the close, with the opening side free to have a shadow.
    Best settings: parameterless; body > 10-bar average body, closing shadow < 10% of the
    average range.
    Edge cases: first 10 bars are 0; +100 white / -100 black; only the closing-side shadow is
    constrained (the opening-side shadow may be long).
    Parity: TA-Lib ``CDLCLOSINGMARUBOZU`` (BodyLong = RealBody/10/1.0, ShadowVeryShort =
    HighLow/10/0.1), exact integer match.
    """

    spec = IndicatorSpec(
        name="closing_marubozu",
        category="candles",
        aliases=("Closing Marubozu", "CDLCLOSINGMARUBOZU"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("closing_marubozu",),
        bounds={"closing_marubozu": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLCLOSINGMARUBOZU",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return closing_marubozu(df)
