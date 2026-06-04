"""CDLSTALLEDPATTERN — Stalled Pattern (three bars, bearish-only).

Three consecutive white candles climbing to consecutively higher closes, but the *advance
stalls*: the first two are long-bodied while the third opens right on the shoulder of the
second's body and has only a small real body — the rally has run out of steam, hinting at a
bearish reversal. TA-Lib emits 0 or **-100** only (no bullish variant, no partial ±80 score).

TA-Lib's exact logic (``ta_CDLSTALLEDPATTERN.c``), for the window ending at bar ``i`` (bars
``i-2``, ``i-1``, ``i``)::

    color(i-2)==white AND color(i-1)==white AND color(i)==white
    AND close(i) > close(i-1) > close(i-2)                       # consecutive higher closes
    AND RealBody(i-2) > BodyLong(i-2)                            # 1st: long real body
    AND RealBody(i-1) > BodyLong(i-1)                            # 2nd: long real body
    AND UpperShadow(i-1) < ShadowVeryShort(i-1)                  # 2nd: very short upper shadow
    AND open(i-1) > open(i-2)                                    # 2nd opens above the 1st open
    AND open(i-1) <= close(i-2) + Near(i-2)                      #     and within/near 1st body
    AND RealBody(i) < BodyShort(i)                               # 3rd: small real body
    AND open(i) >= close(i-1) - RealBody(i) - Near(i-1)          # 3rd rides 2nd's shoulder

where ``BodyLong``/``BodyShort``/``ShadowVeryShort``/``Near`` are the per-bar
:func:`candle_average` thresholds. ``candle_average(df, S).iloc[j]`` reproduces TA-Lib's
``TA_CANDLEAVERAGE(S, …, j)`` (window ending at ``j-1``), so every term is read at the same
array index the C code passes.

The longest averaging period in play is 10 (``BodyLong``/``BodyShort``/``ShadowVeryShort``),
referenced at the earliest at bar ``i-2``; hence ``i-2 >= 10`` ⇒ TA-Lib lookback is 12 (the
first 12 bars are 0).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body, upper_shadow

# TA-Lib reports a lookback of 12 for CDLSTALLEDPATTERN (BodyLong/BodyShort/ShadowVeryShort
# period 10, read at bar i-2 of the three-bar window ⇒ i >= 12). The first 12 outputs are 0.
_LOOKBACK = 12


def stalled_pattern(df: pd.DataFrame) -> pd.Series:
    """Stalled Pattern over ``df`` (OHLC) as a 0/-100 ``Series``.

    Matches ``talib.CDLSTALLEDPATTERN`` bit-exactly: -100 where the three-white-candle advance
    stalls (per the module docstring), 0 otherwise. The first 12 bars are 0 (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    us = upper_shadow(df).to_numpy()
    color = candle_color(df).to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    body_short = candle_average(df, "BodyShort").to_numpy()
    near = candle_average(df, "Near").to_numpy()
    shadow_very_short = candle_average(df, "ShadowVeryShort").to_numpy()

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
    first_long_body = rb[i2] > body_long[i2]
    second_long_body = rb[i1] > body_long[i1]
    second_short_upper = us[i1] < shadow_very_short[i1]
    # 2nd opens above the 1st open and within/near the 1st real body.
    second_in_first = (o[i1] > o[i2]) & (o[i1] <= c[i2] + near[i2])
    # 3rd has a small real body and opens riding the shoulder of the 2nd body.
    third_small_body = rb[i0] < body_short[i0]
    third_on_shoulder = o[i0] >= c[i1] - rb[i0] - near[i1]

    hit = (
        three_white
        & higher_closes
        & first_long_body
        & second_long_body
        & second_short_upper
        & second_in_first
        & third_small_body
        & third_on_shoulder
    )  # NaN thresholds compare False during warm-up

    out[2:] = np.where(hit, -100.0, 0.0)
    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 12 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class StalledPattern(Indicator):
    """Stalled Pattern candlestick.

    What: three rising white candles whose advance stalls — two long bodies then a small
    third body riding the second's shoulder — a bearish reversal warning after an uptrend.
    Best settings: parameterless; bearish-only, so the output is 0 or -100 (never +100).
    Edge cases: first 12 bars are 0 (TA-Lib lookback); no partial ±80 score.
    Parity: TA-Lib ``CDLSTALLEDPATTERN`` (BodyLong/BodyShort/ShadowVeryShort/Near), exact.
    """

    spec = IndicatorSpec(
        name="stalled_pattern",
        category="candles",
        aliases=("StalledPattern", "CDLSTALLEDPATTERN"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("stalled_pattern",),
        bounds={"stalled_pattern": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLSTALLEDPATTERN",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    class Params(BaseModel):
        """No parameters — TA-Lib ``CDLSTALLEDPATTERN`` takes only OHLC (no penetration)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return stalled_pattern(df)
