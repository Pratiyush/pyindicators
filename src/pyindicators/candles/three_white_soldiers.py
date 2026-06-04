"""CDL3WHITESOLDIERS — Three Advancing White Soldiers (three bars, bullish only).

Three consecutive long white candles, each closing higher than the last, each opening within
(or only slightly above) the previous real body, each with a short upper shadow (close near
the high) — a steady, healthy advance. TA-Lib's test (all on bars ``i-2, i-1, i``)::

    white(i-2) AND white(i-1) AND white(i)                       # three white candles
    AND close(i) > close(i-1) > close(i-2)                       # consecutive higher closes
    AND open(i-1) > open(i-2) AND open(i-1) <= close(i-2) + Near(i-2)   # 2nd opens within 1st
    AND open(i)   > open(i-1) AND open(i)   <= close(i-1) + Near(i-1)   # 3rd opens within 2nd
    AND upper_shadow(i-2) < ShadowVeryShort(i-2)                 # short upper shadows
    AND upper_shadow(i-1) < ShadowVeryShort(i-1)
    AND upper_shadow(i)   < ShadowVeryShort(i)
    AND real_body(i-1) > real_body(i-2) - Far(i-2)              # each body not far shorter
    AND real_body(i)   > real_body(i-1) - Far(i-1)
    AND real_body(i)   > BodyShort(i)                            # current body is not short

``Near``/``Far`` are ``(HighLow, 5, 0.2)`` / ``(HighLow, 5, 0.6)``; ``ShadowVeryShort`` is
``(HighLow, 10, 0.1)``; ``BodyShort`` is ``(RealBody, 10, 1.0)``. Output is +100 on a match,
else 0 (this pattern is bullish-only — TA-Lib emits no -100 or partial score). The driving
``ShadowVeryShort``/``BodyShort`` period is 10 and the pattern spans two prior bars, so
TA-Lib's lookback is 12 (the first 12 bars are forced to 0).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body, upper_shadow

# TA-Lib reports a lookback of 12 for CDL3WHITESOLDIERS (period-10 settings + two prior bars).
_LOOKBACK = 12


def three_white_soldiers(df: pd.DataFrame) -> pd.Series:
    """Three Advancing White Soldiers over ``df`` (OHLC) as a 0/100 ``Series``.

    Matches ``talib.CDL3WHITESOLDIERS`` bit-exactly: 100 on a valid three-soldier advance,
    0 otherwise. The first 12 bars are 0 (TA-Lib lookback). Bullish-only (no -100).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    us = upper_shadow(df).to_numpy()
    color = candle_color(df).to_numpy()
    very_short = candle_average(df, "ShadowVeryShort").to_numpy()
    near = candle_average(df, "Near").to_numpy()
    far = candle_average(df, "Far").to_numpy()
    body_short = candle_average(df, "BodyShort").to_numpy()
    n = len(c)
    out = np.zeros(n, dtype="float64")

    # Align the three bars of the window: first = [0..n-3], second = [1..n-2], third = [2..n-1].
    first = slice(0, n - 2)
    second = slice(1, n - 1)
    third = slice(2, n)

    three_white = (color[first] == 1) & (color[second] == 1) & (color[third] == 1)
    higher_closes = (c[third] > c[second]) & (c[second] > c[first])
    second_in_first = (o[second] > o[first]) & (o[second] <= c[first] + near[first])
    third_in_second = (o[third] > o[second]) & (o[third] <= c[second] + near[second])
    short_shadows = (
        (us[first] < very_short[first])
        & (us[second] < very_short[second])
        & (us[third] < very_short[third])
    )
    # Each body not significantly shorter than the previous one (NaN Far -> False during warm-up).
    bodies_grow = (rb[second] > rb[first] - far[first]) & (rb[third] > rb[second] - far[second])
    third_not_short = rb[third] > body_short[third]  # NaN average -> False

    hit = (
        three_white
        & higher_closes
        & second_in_first
        & third_in_second
        & short_shadows
        & bodies_grow
        & third_not_short
    )
    out[2:] = np.where(hit, 100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 12 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class ThreeWhiteSoldiers(Indicator):
    """Three Advancing White Soldiers candlestick pattern.

    What: three long white candles with rising closes, each opening within the prior body and
    closing near its high — a sustained bullish reversal/continuation.
    Best settings: parameterless; "near" opens via Near (HighLow/5/0.2), short upper shadows
    via ShadowVeryShort (HighLow/10/0.1), current body long via BodyShort (RealBody/10/1.0).
    Edge cases: bullish-only (0 or +100, never -100 or a partial score); first 12 bars are 0.
    Parity: TA-Lib ``CDL3WHITESOLDIERS``, exact integer match.
    """

    spec = IndicatorSpec(
        name="three_white_soldiers",
        category="candles",
        aliases=("Three White Soldiers", "CDL3WHITESOLDIERS"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("three_white_soldiers",),
        bounds={"three_white_soldiers": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDL3WHITESOLDIERS",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return three_white_soldiers(df)
