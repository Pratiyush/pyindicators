"""CDLTASUKIGAP — Tasuki Gap (three bars, bidirectional continuation).

A gap is opened by the first candle, a second same-coloured candle continues through the gap,
and a third opposite-coloured candle of (roughly) the same body size opens inside the second
body and closes into — but not through — the gap, leaving it unfilled. TA-Lib::

    # upside (bullish continuation, +100)
    body_lo[i-1] > body_hi[i-2]                       # candle i-1 gaps up over i-2
    AND color(i-1) == white AND color(i) == black
    AND open(i) < close(i-1) AND open(i) > open(i-1)  # i opens within the white body
    AND close(i) < open(i-1) AND close(i) > body_hi[i-2]  # i closes inside the gap
    AND |RealBody(i-1) - RealBody(i)| < Near average(i-1)  # ~same body size

    # downside (bearish continuation, -100): the mirror image
    body_hi[i-1] < body_lo[i-2]
    AND color(i-1) == black AND color(i) == white
    AND open(i) < open(i-1) AND open(i) > close(i-1)
    AND close(i) > open(i-1) AND close(i) < body_lo[i-2]
    AND |RealBody(i-1) - RealBody(i)| < Near average(i-1)

Sign is the colour of the gapping candle ``i-1`` (white -> +100, black -> -100). This is a
pure ±100 / 0 signal: the only tolerance band (``Near``) uses a **strict** ``<`` comparison,
so TA-Lib emits **no** ±80 partial-penetration score here.

``Near`` is ``(HighLow, 5, 0.2)``, read at the gapping candle ``i-1`` (window ending at
``i-2``). TA-Lib's lookback is ``Near=5 + 2 = 7`` — the ``+2`` from the two earlier candles the
pattern spans — so the first 7 bars are forced to 0.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body

# TA-Lib reports a lookback of 7 for CDLTASUKIGAP: Near=5 + 2, the +2 from the two earlier
# candles the pattern spans (the pre-gap candle i-2 and the gapping candle i-1).
_LOOKBACK = 7


def tasuki_gap(df: pd.DataFrame) -> pd.Series:
    """Tasuki Gap pattern over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDLTASUKIGAP`` bit-exactly: +100 on an upside (bullish) tasuki gap, -100 on
    a downside (bearish) one, 0 otherwise. The first 7 bars are 0 (TA-Lib lookback). Output is
    pure ±100/0 — the ``Near`` body-size band is a strict ``<``, so there is no ±80 partial
    score.
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    near = candle_average(df, "Near").to_numpy()
    body_hi = np.maximum(o, c)
    body_lo = np.minimum(o, c)
    color = candle_color(df).to_numpy()
    n = len(c)
    out = np.zeros(n, dtype="float64")

    # Output at i spans three candles: i-2 (pre-gap), i-1 (gapping candle), i (continuation).
    # The Near average is read at the gapping candle, i-1 (its window ends at i-2).
    pre = slice(0, n - 2)
    gap = slice(1, n - 1)
    cur = slice(2, n)
    near1 = near[gap]
    body_diff = np.abs(rb[gap] - rb[cur])

    # Upside (bullish): white candle gaps up, black candle opens within it and closes into gap.
    up = (
        (body_lo[gap] > body_hi[pre])
        & (color[gap] == 1)
        & (color[cur] == -1)
        & (o[cur] < c[gap])
        & (o[cur] > o[gap])
        & (c[cur] < o[gap])
        & (c[cur] > body_hi[pre])
    )
    # Downside (bearish): the mirror image with a black gapping candle.
    down = (
        (body_hi[gap] < body_lo[pre])
        & (color[gap] == -1)
        & (color[cur] == 1)
        & (o[cur] < o[gap])
        & (o[cur] > c[gap])
        & (c[cur] > o[gap])
        & (c[cur] < body_lo[pre])
    )
    same_size = body_diff < near1  # NaN average -> False during warm-up; strict < (no ±80)
    hit = (up | down) & same_size
    out[2:] = np.where(hit, color[gap] * 100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 7 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class TasukiGap(Indicator):
    """Tasuki Gap candlestick pattern.

    What: a gap opened by one candle, continued by a same-colour candle, then a same-size
    opposite-colour candle that closes into but not through the gap — a continuation signal
    (bullish on an upside gap, bearish on a downside gap).
    Best settings: parameterless; bodies "near" equal (Near = HighLow/5/0.2).
    Edge cases: pure ±100/0 (no ±80 partial score); first 7 bars are 0 (TA-Lib lookback).
    Parity: TA-Lib ``CDLTASUKIGAP`` (Near = HighLow/5/0.2), exact integer match.
    """

    class Params(BaseModel):
        """No parameters: CDLTASUKIGAP is fully determined (no penetration argument)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec = IndicatorSpec(
        name="tasuki_gap",
        category="candles",
        aliases=("TasukiGap", "CDLTASUKIGAP"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("tasuki_gap",),
        bounds={"tasuki_gap": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLTASUKIGAP",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return tasuki_gap(df)
