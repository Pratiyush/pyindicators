"""CDLHARAMI — Harami pattern (two bars, bidirectional).

A small current body sits *inside* a long previous body of the opposite tendency. TA-Lib::

    RealBody(prev) > BodyLong average(prev)        # long previous body
    AND RealBody(cur) < BodyShort average(cur)     # short current body
    AND max(open, close)[cur] <= max(open, close)[prev]   # current body within previous
    AND min(open, close)[cur] >= min(open, close)[prev]

with **at least one** containment edge strictly inside (a current body sharing both edges is
not a harami). The magnitude is 100 when *both* edges are strictly inside, **80** when exactly
one edge touches the previous body. Sign is the *opposite* of the previous candle's colour
(bullish harami follows a black candle).

Both ``BodyLong`` and ``BodyShort`` are ``(RealBody, 10, 1.0)``. The previous body's long-body
average needs 10 prior bars, so TA-Lib's lookback is 11 (the first 11 bars are 0).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body

# TA-Lib reports a lookback of 11 for CDLHARAMI (BodyLong period 10 on the previous bar).
_LOOKBACK = 11


def harami(df: pd.DataFrame) -> pd.Series:
    """Harami pattern over ``df`` (OHLC) as a -100/-80/0/80/100 ``Series``.

    Matches ``talib.CDLHARAMI`` bit-exactly, including the ±80 partial score when exactly one
    containment edge touches the previous body. The first 11 bars are 0 (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    body_short = candle_average(df, "BodyShort").to_numpy()
    body_hi = np.maximum(o, c)
    body_lo = np.minimum(o, c)
    color = candle_color(df).to_numpy()
    n = len(c)
    out = np.zeros(n, dtype="float64")

    # Previous = bars [0..n-2], current = bars [1..n-1].
    long_prev = rb[:-1] > body_long[:-1]
    short_cur = rb[1:] < body_short[1:]
    incl = (body_hi[1:] <= body_hi[:-1]) & (body_lo[1:] >= body_lo[:-1])
    both = (body_hi[1:] < body_hi[:-1]) & (body_lo[1:] > body_lo[:-1])
    any_strict = (body_hi[1:] < body_hi[:-1]) | (body_lo[1:] > body_lo[:-1])

    hit = long_prev & short_cur & incl & any_strict  # NaN average -> False
    sign = -color[:-1]  # opposite of previous candle's colour
    magnitude = np.where(both, 100.0, 80.0)
    out[1:] = np.where(hit, sign * magnitude, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 11 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class Harami(Indicator):
    """Harami candlestick pattern.

    What: a small body contained within the prior long body — a reversal/indecision signal.
    Best settings: parameterless; bullish after a black candle, bearish after a white one.
    Edge cases: ±80 when exactly one containment edge touches; first 11 bars are 0.
    Parity: TA-Lib ``CDLHARAMI`` (BodyLong/BodyShort = RealBody/10/1.0, ±80 partial), exact.
    """

    spec = IndicatorSpec(
        name="harami",
        category="candles",
        aliases=("Harami", "CDLHARAMI"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("harami",),
        bounds={"harami": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLHARAMI",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return harami(df)
