"""CDL3BLACKCROWS — Three Black Crows pattern (four bars, bearish-only).

Three consecutive long-ish black candles, each closing lower than the last, each opening
*inside* the previous candle's real body, each with a very short lower shadow, following a
white candle whose high tops the first crow's close. A classic top-reversal. TA-Lib::

    color(i-3) ==  1                                   # a prior white candle
    color(i-2) == -1 AND lower_shadow(i-2) < ShadowVeryShort avg(i-2)   # 1st black crow
    color(i-1) == -1 AND lower_shadow(i-1) < ShadowVeryShort avg(i-1)   # 2nd black crow
    color(i)   == -1 AND lower_shadow(i)   < ShadowVeryShort avg(i)     # 3rd black crow
    open(i-1) < open(i-2) AND open(i-1) > close(i-2)   # 2nd opens within 1st body
    open(i)   < open(i-1) AND open(i)   > close(i-1)   # 3rd opens within 2nd body
    high(i-3) > close(i-2)                             # 1st crow closes below prior high
    close(i-2) > close(i-1) AND close(i-1) > close(i)  # progressively lower closes

This is a one-sided (bearish) pattern: the output is **only -100 or 0** — no bullish variant
and no ±80 partial-penetration score. ``ShadowVeryShort`` is ``(HighLow, 10, 0.1)``; with the
extra three prior-bar offset, TA-Lib's lookback is 10 + 3 = 13 (the first 13 bars are 0).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, lower_shadow

# TA-Lib reports a lookback of 13 for CDL3BLACKCROWS (ShadowVeryShort period 10 + 3 prior bars).
_LOOKBACK = 13


def three_black_crows(df: pd.DataFrame) -> pd.Series:
    """Three Black Crows over ``df`` (OHLC) as a -100/0 ``Series``.

    Matches ``talib.CDL3BLACKCROWS`` bit-exactly: -100 where the four-bar bearish pattern
    forms, 0 elsewhere. The first 13 bars are 0 (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    h = df[HIGH].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    color = candle_color(df).to_numpy()
    ls = lower_shadow(df).to_numpy()
    svs = candle_average(df, "ShadowVeryShort").to_numpy()
    n = len(c)
    out = np.zeros(n, dtype="float64")

    if n > _LOOKBACK:
        # Current bar i runs over [3 .. n-1]; the prior white candle is bar i-3.
        i = np.arange(3, n)
        i1 = i - 1
        i2 = i - 2
        i3 = i - 3

        hit = (
            (color[i3] == 1)
            & (color[i2] == -1)
            & (ls[i2] < svs[i2])
            & (color[i1] == -1)
            & (ls[i1] < svs[i1])
            & (color[i] == -1)
            & (ls[i] < svs[i])
            & (o[i1] < o[i2])
            & (o[i1] > c[i2])
            & (o[i] < o[i1])
            & (o[i] > c[i1])
            & (h[i3] > c[i2])
            & (c[i2] > c[i1])
            & (c[i1] > c[i])
        )
        out[3:] = np.where(hit, -100.0, 0.0)  # NaN ShadowVeryShort avg -> False -> 0

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 13 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class ThreeBlackCrows(Indicator):
    """Three Black Crows candlestick pattern.

    What: three consecutive lower-closing black candles, each opening inside the prior body
    with a tiny lower shadow, after a white candle — a strong bearish top reversal.
    Best settings: parameterless; ``ShadowVeryShort`` body threshold is 10% of the 10-bar range.
    Edge cases: bearish-only (output is -100 or 0, never +100/±80); first 13 bars are 0.
    Parity: TA-Lib ``CDL3BLACKCROWS`` (ShadowVeryShort = HighLow/10/0.1), exact integer match.
    """

    spec = IndicatorSpec(
        name="three_black_crows",
        category="candles",
        aliases=("ThreeBlackCrows", "CDL3BLACKCROWS"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("three_black_crows",),
        bounds={"three_black_crows": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDL3BLACKCROWS",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return three_black_crows(df)
