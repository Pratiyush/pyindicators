"""CDL2CROWS — Two Crows pattern (three bars, bearish only).

A bearish reversal at the top of an uptrend: a long white candle, then a black candle that
gaps its body above the first, then a second black candle that opens *inside* the prior
black body and closes back *inside* the first white body (the two "crows" erasing the gain).
TA-Lib's ``CDL2CROWS``::

    1st candle: white AND RealBody(1st) > BodyLong average(1st)      # long white
    2nd candle: black AND body gaps up over the 1st body            # min(o,c)[2nd] > max(o,c)[1st]
    3rd candle: black                                               # black
                AND open(3rd) < open(2nd) AND open(3rd) > close(2nd) # opens within 2nd body
                AND close(3rd) > open(1st) AND close(3rd) < close(1st)# closes within 1st body

Every edge is a strict inequality, so a body that merely *touches* a boundary does not
qualify — there is no partial-penetration score here; the output is only -100 or 0 (TA-Lib
emits no bullish variant and no ±80 for this pattern).

``BodyLong`` is ``(RealBody, 10, 1.0)`` and is evaluated on the *first* candle (two bars
back), so TA-Lib's lookback is ``10 + 2 = 12`` (the first 12 bars are 0).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body

# TA-Lib reports a lookback of 12 for CDL2CROWS (BodyLong period 10 on the first of 3 bars).
_LOOKBACK = 12


def two_crows(df: pd.DataFrame) -> pd.Series:
    """Two Crows pattern over ``df`` (OHLC) as a -100/0 ``Series``.

    Matches ``talib.CDL2CROWS`` bit-exactly: -100 at the third bar of a Two Crows formation,
    0 elsewhere. All comparisons are strict, so there is no ±80 partial score. The first 12
    bars are 0 (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    color = candle_color(df).to_numpy()
    body_hi = np.maximum(o, c)
    body_lo = np.minimum(o, c)
    n = len(c)
    out = np.zeros(n, dtype="float64")

    # Triplet (1st, 2nd, 3rd) = bars (i-2, i-1, i) for i in [2 .. n-1].
    first_white_long = (color[:-2] == 1) & (rb[:-2] > body_long[:-2])  # NaN average -> False
    second_black_gap = (color[1:-1] == -1) & (body_lo[1:-1] > body_hi[:-2])
    third_black = color[2:] == -1
    opens_in_second = (o[2:] < o[1:-1]) & (o[2:] > c[1:-1])
    closes_in_first = (c[2:] > o[:-2]) & (c[2:] < c[:-2])

    hit = first_white_long & second_black_gap & third_black & opens_in_second & closes_in_first
    out[2:] = np.where(hit, -100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 12 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class TwoCrows(Indicator):
    """Two Crows candlestick pattern.

    What: a long white candle, then a gapped-up black candle, then a black candle that opens
        inside the second body and closes inside the first — a bearish reversal at a top.
    Best settings: parameterless; the signal is bearish only (-100) or absent (0).
    Edge cases: every edge is strict, so a touching boundary gives 0 (no ±80); first 12 bars
        are 0 (TA-Lib lookback = BodyLong period 10 on the first of three bars + 2).
    Parity: TA-Lib ``CDL2CROWS`` (BodyLong = RealBody/10/1.0), exact integer match.
    """

    spec = IndicatorSpec(
        name="two_crows",
        category="candles",
        aliases=("TwoCrows", "CDL2CROWS"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("two_crows",),
        bounds={"two_crows": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDL2CROWS",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return two_crows(df)
