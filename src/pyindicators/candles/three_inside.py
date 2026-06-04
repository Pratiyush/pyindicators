"""CDL3INSIDE — Three Inside Up/Down (three bars, bidirectional).

A harami (a short body engulfed by a prior long body) confirmed by a third candle that closes
in the opposite direction of the first. TA-Lib's exact test for bar ``i`` (the 3rd candle)::

    RealBody(i-2) > BodyLong  average(i-2)               # 1st: long body
    AND RealBody(i-1) <= BodyShort average(i-1)          # 2nd: short body
    AND max(open, close)[i-1] < max(open, close)[i-2]    # 2nd engulfed by the 1st body
    AND min(open, close)[i-1] > min(open, close)[i-2]
    AND (
        # Three Inside Up (+):  1st black, 3rd white, 3rd closes above the 1st open
        ( color(i-2) == -1 AND color(i) == 1  AND close(i) > open(i-2) )
        OR
        # Three Inside Down (-): 1st white, 3rd black, 3rd closes below the 1st open
        ( color(i-2) ==  1 AND color(i) == -1 AND close(i) < open(i-2) )
    )

Output is ``-color(i-2) * 100`` — +100 for the bullish "up" variant (1st candle black), -100
for the bearish "down" variant (1st candle white), 0 otherwise. Unlike harami/engulfing this
pattern emits no ±80 partial score: it is a pure -100/0/100 signal (verified against TA-Lib on
synthetic and real AAPL bars).

Both ``BodyLong`` and ``BodyShort`` are ``(RealBody, 10, 1.0)``. The 1st candle's long-body
average needs the 10 bars ending at ``i-3``, and the pattern spans two more bars, so TA-Lib's
lookback is 12 (the first 12 outputs are always 0).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body

# TA-Lib reports a lookback of 12 for CDL3INSIDE (BodyLong period 10 + the two prior bars).
_LOOKBACK = 12


def three_inside(df: pd.DataFrame) -> pd.Series:
    """Three Inside Up/Down over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDL3INSIDE`` bit-exactly: +100 for the bullish "up" variant, -100 for the
    bearish "down" variant, 0 elsewhere. The first 12 bars are 0 (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    body_short = candle_average(df, "BodyShort").to_numpy()
    color = candle_color(df).to_numpy()
    body_hi = np.maximum(o, c)
    body_lo = np.minimum(o, c)
    n = len(c)
    out = np.zeros(n, dtype="float64")

    # 1st candle = bars [0..n-3], 2nd = [1..n-2], 3rd (current) = [2..n-1].
    first_long = rb[:-2] > body_long[:-2]  # NaN average -> False during warm-up
    second_short = rb[1:-1] <= body_short[1:-1]
    engulfed = (body_hi[1:-1] < body_hi[:-2]) & (body_lo[1:-1] > body_lo[:-2])
    col_first = color[:-2]
    col_third = color[2:]
    # 3rd candle closes opposite to the 1st candle's direction.
    up = (col_first == -1) & (col_third == 1) & (c[2:] > o[:-2])
    down = (col_first == 1) & (col_third == -1) & (c[2:] < o[:-2])

    hit = first_long & second_short & engulfed & (up | down)
    out[2:] = np.where(hit, -col_first * 100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 12 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class ThreeInside(Indicator):
    """Three Inside Up/Down candlestick pattern.

    What: a harami confirmed by a third candle closing opposite the first — a reversal signal.
    Best settings: parameterless; +100 "up" (1st black), -100 "down" (1st white).
    Edge cases: pure -100/0/100 (no ±80 partial); first 12 bars are 0 (TA-Lib lookback).
    Parity: TA-Lib ``CDL3INSIDE`` (BodyLong/BodyShort = RealBody/10/1.0), exact integer match.
    """

    spec = IndicatorSpec(
        name="three_inside",
        category="candles",
        aliases=("ThreeInside", "CDL3INSIDE"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("three_inside",),
        bounds={"three_inside": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDL3INSIDE",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return three_inside(df)
