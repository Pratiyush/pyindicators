"""CDLADVANCEBLOCK — Advance Block pattern (three bars, bearish-only).

Three consecutive white candles, each closing higher than the last and each opening within
(or near) the previous real body, but with the *advance weakening* — the bodies shrink and/or
the upper shadows lengthen, hinting the uptrend is running out of steam. TA-Lib emits 0 or
**-100** only (there is no bullish variant and no partial ±80 score).

TA-Lib's exact logic (``ta_CDLADVANCEBLOCK.c``), for the window ending at bar ``i`` (bars
``i-2``, ``i-1``, ``i``)::

    color(i-2)==white AND color(i-1)==white AND color(i)==white
    AND close(i) > close(i-1) > close(i-2)                       # consecutive higher closes
    AND open(i-1) > open(i-2) AND open(i-1) <= close(i-2) + Near(i-2)   # 2nd opens in 1st body
    AND open(i)   > open(i-1) AND open(i)   <= close(i-1) + Near(i-1)   # 3rd opens in 2nd body
    AND RealBody(i-2) > BodyLong(i-2)                            # 1st: long real body
    AND UpperShadow(i-2) < ShadowShort(i-2)                      # 1st: short upper shadow
    AND (   # advance is deteriorating — any one of:
              ( RealBody(i-1) < RealBody(i-2) - Far(i-2)
                AND RealBody(i) < RealBody(i-1) + Near(i-1) )            # 2 far < 1, 3 ~<= 2
           OR RealBody(i) < RealBody(i-1) - Far(i-1)                     # 3 far < 2
           OR ( RealBody(i) < RealBody(i-1) AND RealBody(i-1) < RealBody(i-2)
                AND ( UpperShadow(i) > ShadowShort(i)
                      OR UpperShadow(i-1) > ShadowShort(i-1) ) )         # shrinking + long wick
           OR ( RealBody(i) < RealBody(i-1)
                AND UpperShadow(i) > ShadowLong(i) )                     # 3rd has long upper wick
        )

where ``Near``/``Far``/``BodyLong``/``ShadowShort``/``ShadowLong`` are the per-bar
:func:`candle_average` thresholds. ``candle_average(df, S).iloc[j]`` reproduces TA-Lib's
``TA_CANDLEAVERAGE(S, …, j)`` (window ending at ``j-1``), so every term is read at the same
array index the C code passes.

The longest averaging period in play is 10 (``BodyLong``/``ShadowShort``), referenced at the
earliest at bar ``i-2``; hence ``i-2 >= 10`` ⇒ TA-Lib lookback is 12 (the first 12 bars are 0).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body, upper_shadow

# TA-Lib reports a lookback of 12 for CDLADVANCEBLOCK (BodyLong/ShadowShort period 10, read at
# bar i-2 of the three-bar window ⇒ i >= 12). The first 12 outputs are always 0.
_LOOKBACK = 12


def advance_block(df: pd.DataFrame) -> pd.Series:
    """Advance Block pattern over ``df`` (OHLC) as a 0/-100 ``Series``.

    Matches ``talib.CDLADVANCEBLOCK`` bit-exactly: -100 where the three-white-candle advance is
    weakening (per the module docstring), 0 otherwise. The first 12 bars are 0 (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    us = upper_shadow(df).to_numpy()
    color = candle_color(df).to_numpy()
    near = candle_average(df, "Near").to_numpy()
    far = candle_average(df, "Far").to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    shadow_short = candle_average(df, "ShadowShort").to_numpy()
    shadow_long = candle_average(df, "ShadowLong").to_numpy()

    n = len(c)
    out = np.zeros(n, dtype="float64")
    if n <= _LOOKBACK:
        return pd.Series(out, index=df.index)

    # Index slices for the three-bar window: i2 = i-2 (first), i1 = i-1 (second), i0 = i (third).
    i2 = slice(0, n - 2)
    i1 = slice(1, n - 1)
    i0 = slice(2, n)

    three_white = (color[i2] == 1) & (color[i1] == 1) & (color[i0] == 1)
    higher_closes = (c[i0] > c[i1]) & (c[i1] > c[i2])
    second_in_first = (o[i1] > o[i2]) & (o[i1] <= c[i2] + near[i2])
    third_in_second = (o[i0] > o[i1]) & (o[i0] <= c[i1] + near[i1])
    first_long_body = rb[i2] > body_long[i2]
    first_short_upper = us[i2] < shadow_short[i2]

    # Advance is deteriorating — any one of the four TA-Lib clauses.
    deteriorate = (
        ((rb[i1] < rb[i2] - far[i2]) & (rb[i0] < rb[i1] + near[i1]))
        | (rb[i0] < rb[i1] - far[i1])
        | (
            (rb[i0] < rb[i1])
            & (rb[i1] < rb[i2])
            & ((us[i0] > shadow_short[i0]) | (us[i1] > shadow_short[i1]))
        )
        | ((rb[i0] < rb[i1]) & (us[i0] > shadow_long[i0]))
    )

    hit = (
        three_white
        & higher_closes
        & second_in_first
        & third_in_second
        & first_long_body
        & first_short_upper
        & deteriorate
    )  # NaN thresholds compare False during warm-up

    out[2:] = np.where(hit, -100.0, 0.0)
    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 12 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class AdvanceBlock(Indicator):
    """Advance Block candlestick pattern.

    What: three rising white candles whose advance is weakening (shrinking bodies and/or
    growing upper shadows) — a bearish reversal warning after an uptrend.
    Best settings: parameterless; bearish-only, so the output is 0 or -100 (never +100).
    Edge cases: first 12 bars are 0 (TA-Lib lookback); no partial ±80 score.
    Parity: TA-Lib ``CDLADVANCEBLOCK`` (BodyLong/ShadowShort/ShadowLong/Near/Far), exact.
    """

    spec = IndicatorSpec(
        name="advance_block",
        category="candles",
        aliases=("AdvanceBlock", "CDLADVANCEBLOCK"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("advance_block",),
        bounds={"advance_block": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLADVANCEBLOCK",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return advance_block(df)
