"""CDLDOJISTAR — Doji Star pattern (two bars, bidirectional).

A long real body is followed by a doji (negligible body) that *gaps* away from it — a
classic reversal star. TA-Lib::

    RealBody(prev) > BodyLong average(prev)         # long previous body
    AND RealBody(cur) <= BodyDoji average(cur)      # current body is a doji
    AND (
        ( color(prev) == white AND realbody-gap-up(cur, prev) )      # star above a white body
        OR
        ( color(prev) == black AND realbody-gap-down(cur, prev) )    # star below a black body
    )

where the real-body gap is strict: gap up needs ``min(open, close)[cur] > max(open, close)[prev]``
and gap down needs ``max(open, close)[cur] < min(open, close)[prev]``. The sign is the *opposite*
of the previous candle's colour (a doji star after a white body is bearish, -100), so the output
is the pure integer ``-color(prev) * 100`` — there is no ±80 partial-penetration score for this
pattern.

``BodyLong`` is ``(RealBody, 10, 1.0)`` and ``BodyDoji`` is ``(HighLow, 10, 0.1)``. TA-Lib's
lookback is ``max(10, 10) + 1 = 11`` (the long-body average needs 10 bars ending at the previous
bar), so the first 11 bars are forced to 0.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body

# TA-Lib reports a lookback of max(BodyDoji, BodyLong) + 1 = 11 for CDLDOJISTAR.
_LOOKBACK = 11


def doji_star(df: pd.DataFrame) -> pd.Series:
    """Doji Star pattern over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDLDOJISTAR`` bit-exactly: a long previous body followed by a doji that
    gaps away from it, signed opposite to the previous candle's colour. The first 11 bars are
    0 (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    body_doji = candle_average(df, "BodyDoji").to_numpy()
    body_hi = np.maximum(o, c)
    body_lo = np.minimum(o, c)
    color = candle_color(df).to_numpy()
    n = len(c)
    out = np.zeros(n, dtype="float64")

    # Previous = bars [0..n-2], current = bars [1..n-1].
    long_prev = rb[:-1] > body_long[:-1]  # NaN average -> False during warm-up
    doji_cur = rb[1:] <= body_doji[1:]
    gap_up = body_lo[1:] > body_hi[:-1]  # strict real-body gap up over the previous body
    gap_down = body_hi[1:] < body_lo[:-1]  # strict real-body gap down under the previous body

    prev_white = color[:-1] == 1
    prev_black = color[:-1] == -1
    gapped = (prev_white & gap_up) | (prev_black & gap_down)

    hit = long_prev & doji_cur & gapped
    out[1:] = np.where(hit, -color[:-1] * 100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 11 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class DojiStar(Indicator):
    """Doji Star candlestick pattern.

    What: a long body then a gapped doji — an indecision star signalling a likely reversal.
    Best settings: parameterless; bearish (-100) after a white body, bullish (+100) after black.
    Edge cases: the gap is strict (bodies must not touch); first 11 bars are 0; output is pure
    ±100 (no ±80 partial score for this pattern).
    Parity: TA-Lib ``CDLDOJISTAR`` (BodyLong = RealBody/10/1.0, BodyDoji = HighLow/10/0.1), exact.
    """

    class Params(BaseModel):
        """Parameters for Doji Star (TA-Lib ``CDLDOJISTAR`` takes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="doji_star",
        category="candles",
        aliases=("DojiStar", "CDLDOJISTAR"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("doji_star",),
        bounds={"doji_star": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLDOJISTAR",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return doji_star(df)
