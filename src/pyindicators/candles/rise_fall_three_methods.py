"""CDLRISEFALL3METHODS — Rising/Falling Three Methods (five bars, bidirectional).

A five-candle *continuation* pattern: a long candle, three small counter-trend candles that
stay within the long candle's range, then another long candle in the original direction that
closes past the first candle's close. TA-Lib's test (``i`` is the 5th candle; mirror image for
the two directions, driven by the 1st candle's colour ``col1 = candle_color(i-4)``)::

    RealBody(i-4) > BodyLong  average(i-4)        # 1st candle long
    RealBody(i-3) < BodyShort average(i-3)        # 2nd/3rd/4th candles short
    RealBody(i-2) < BodyShort average(i-2)
    RealBody(i-1) < BodyShort average(i-1)
    RealBody(i)   > BodyLong  average(i)          # 5th candle long

    color(i-4) == -color(i-3)                     # white, 3 black, white  ||
    color(i-3) ==  color(i-2)                     #   black, 3 white, black
    color(i-2) ==  color(i-1)
    color(i-1) == -color(i)

    # the 2nd/3rd/4th bodies stay within the 1st candle's high-low range
    min(open,close)[i-3] < high[i-4] AND max(open,close)[i-3] > low[i-4]
    min(open,close)[i-2] < high[i-4] AND max(open,close)[i-2] > low[i-4]
    min(open,close)[i-1] < high[i-4] AND max(open,close)[i-1] > low[i-4]

    # the 2nd/3rd/4th close trends *against* the 1st candle (falls in a rising pattern)
    close[i-2] * col1 < close[i-3] * col1
    close[i-1] * col1 < close[i-2] * col1

    open[i]  * col1 > close[i-1] * col1           # 5th opens beyond the 4th close
    close[i] * col1 > close[i-4] * col1           # 5th closes beyond the 1st close

The sign TA-Lib emits is the **1st** candle's colour (``candle_color(i-4) * 100``): the rising
variant (white/black/black/black/white) scores +100, the falling variant scores -100. Output
is strictly -100/0/100 — every clause is a strict inequality, so there is no ±80 partial score.

``BodyLong`` and ``BodyShort`` are both ``(RealBody, 10, 1.0)``; their averages use the 10 bars
ending one before the candle they size, and the pattern spans 4 prior bars, so TA-Lib's
lookback is ``max(10, 10) + 4 = 14`` — the first 14 bars are forced to 0.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body

# TA-Lib reports a lookback of 14 for CDLRISEFALL3METHODS (max(BodyLong, BodyShort)=10 + 4).
_LOOKBACK = 14


def rise_fall_three_methods(df: pd.DataFrame) -> pd.Series:
    """Rising/Falling Three Methods over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDLRISEFALL3METHODS`` bit-exactly. The sign is the first (long) candle's
    colour, so the rising variant scores +100 and the falling variant -100; the first 14 bars
    are 0 (TA-Lib lookback). No ±80 partial score for this pattern.
    """
    o = df[OPEN].to_numpy(dtype="float64")
    h = df[HIGH].to_numpy(dtype="float64")
    low = df[LOW].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    color = candle_color(df).to_numpy()
    rb = real_body(df).to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    body_short = candle_average(df, "BodyShort").to_numpy()
    body_hi = np.maximum(o, c)
    body_lo = np.minimum(o, c)

    n = len(c)
    out = np.zeros(n, dtype="float64")
    if n <= _LOOKBACK:
        return pd.Series(out, index=df.index)

    # Align the five candles: index i is the 5th candle, i-4 the 1st (windowed from _LOOKBACK).
    i = np.arange(_LOOKBACK, n)
    c1, c2, c3, c4, c5 = i - 4, i - 3, i - 2, i - 1, i
    col1 = color[c1]  # the 1st candle's colour drives the sign and the trend-direction tests.

    # Body sizes: 1st and 5th long, 2nd/3rd/4th short (NaN averages -> False during warm-up).
    long_first = rb[c1] > body_long[c1]
    short_mid = (
        (rb[c2] < body_short[c2]) & (rb[c3] < body_short[c3]) & (rb[c4] < body_short[c4])
    )
    long_last = rb[c5] > body_long[c5]

    # Colours: 1st == -2nd, 2nd == 3rd == 4th, 4th == -5th (white,3black,white || mirror).
    colors_ok = (
        (col1 == -color[c2])
        & (color[c2] == color[c3])
        & (color[c3] == color[c4])
        & (color[c4] == -color[c5])
    )

    # 2nd/3rd/4th bodies stay within the 1st candle's high-low range.
    within = (
        (body_lo[c2] < h[c1]) & (body_hi[c2] > low[c1])
        & (body_lo[c3] < h[c1]) & (body_hi[c3] > low[c1])
        & (body_lo[c4] < h[c1]) & (body_hi[c4] > low[c1])
    )

    # 2nd/3rd/4th closes trend against the 1st candle; 5th opens/closes beyond (× col1 ∈ ±1).
    trend = (c[c3] * col1 < c[c2] * col1) & (c[c4] * col1 < c[c3] * col1)
    fifth = (o[c5] * col1 > c[c4] * col1) & (c[c5] * col1 > c[c1] * col1)

    hit = long_first & short_mid & long_last & colors_ok & within & trend & fifth
    out[_LOOKBACK:] = np.where(hit, col1 * 100.0, 0.0)
    return pd.Series(out, index=df.index)


@INDICATORS.register
class RiseFallThreeMethods(Indicator):
    """Rising/Falling Three Methods candlestick pattern.

    What: a five-bar continuation — a long candle, three small counter-trend candles held
    inside its range, then a long candle resuming the trend past the first candle's close.
    Best settings: parameterless; 1st/5th bodies long (> 10-bar average), 2nd/3rd/4th short.
    Edge cases: first 14 bars are 0; sign is the first candle's colour, so the rising variant
    scores +100 and the falling variant -100 (no ±80 partial score).
    Parity: TA-Lib ``CDLRISEFALL3METHODS`` (BodyLong/BodyShort = RealBody/10/1.0), exact.
    """

    class Params(BaseModel):
        """Rising/Falling Three Methods takes no parameters (TA-Lib has none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec = IndicatorSpec(
        name="rise_fall_three_methods",
        category="candles",
        aliases=("Rising/Falling Three Methods", "CDLRISEFALL3METHODS"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("rise_fall_three_methods",),
        bounds={"rise_fall_three_methods": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLRISEFALL3METHODS",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return rise_fall_three_methods(df)
