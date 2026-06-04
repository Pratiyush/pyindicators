"""CDLUPSIDEGAP2CROWS — Upside Gap Two Crows (three bars, bearish only).

A bearish reversal in an uptrend: a long white candle, then a black candle whose body gaps
*up* above the first (the upside gap), then a second black candle that opens even higher than
the first crow yet closes back down into the gap — still above the first candle's close, so
the upside gap is never fully filled (the two "crows" only nibble at the prior advance).
TA-Lib's ``CDLUPSIDEGAP2CROWS``::

    1st candle: white AND RealBody(1st) > BodyLong average(1st)       # long white
    2nd candle: black AND body gaps up over the 1st body             # min(o,c)[2nd] > max(o,c)[1st]
    3rd candle: black                                                # black
                AND open(3rd)  > open(2nd)                           # opens above the 2nd open
                AND close(3rd) < close(2nd)                          # closes below the 2nd close
                AND close(3rd) > close(1st)                          # still above the 1st close

Every edge is a strict inequality, so a body that merely *touches* a boundary does not
qualify — there is no partial-penetration score here; the output is only -100 or 0 (TA-Lib
emits no bullish variant and no ±80 for this pattern).

``BodyLong`` is ``(RealBody, 10, 1.0)`` and is evaluated on the *first* candle (two bars
back), so TA-Lib's lookback is ``10 + 2 = 12`` (the first 12 bars are 0).
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body

# TA-Lib reports a lookback of 12 for CDLUPSIDEGAP2CROWS (BodyLong period 10 on the 1st of 3 bars).
_LOOKBACK = 12


def upside_gap_two_crows(df: pd.DataFrame) -> pd.Series:
    """Upside Gap Two Crows over ``df`` (OHLC) as a -100/0 ``Series``.

    Matches ``talib.CDLUPSIDEGAP2CROWS`` bit-exactly: -100 at the third bar of an Upside Gap
    Two Crows formation, 0 elsewhere. All comparisons are strict, so there is no ±80 partial
    score. The first 12 bars are 0 (TA-Lib lookback).
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
    opens_above_second = o[2:] > o[1:-1]
    closes_below_second = c[2:] < c[1:-1]
    closes_above_first = c[2:] > c[:-2]

    hit = (
        first_white_long
        & second_black_gap
        & third_black
        & opens_above_second
        & closes_below_second
        & closes_above_first
    )
    out[2:] = np.where(hit, -100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 12 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class UpsideGapTwoCrows(Indicator):
    """Upside Gap Two Crows candlestick pattern.

    What: a long white candle, then a black candle gapping up over its body, then a black
        candle that opens higher still yet closes back into the gap (above the first close) —
        a bearish reversal at a top where the gap is never filled.
    Best settings: parameterless; the signal is bearish only (-100) or absent (0).
    Edge cases: every edge is strict, so a touching boundary gives 0 (no ±80); first 12 bars
        are 0 (TA-Lib lookback = BodyLong period 10 on the first of three bars + 2).
    Parity: TA-Lib ``CDLUPSIDEGAP2CROWS`` (BodyLong = RealBody/10/1.0), exact integer match.
    """

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="upside_gap_two_crows",
        category="candles",
        aliases=("UpsideGapTwoCrows", "CDLUPSIDEGAP2CROWS"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("upside_gap_two_crows",),
        bounds={"upside_gap_two_crows": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLUPSIDEGAP2CROWS",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return upside_gap_two_crows(df)
