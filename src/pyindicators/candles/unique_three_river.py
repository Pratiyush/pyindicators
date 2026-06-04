"""CDLUNIQUE3RIVER — Unique Three River pattern (three bars, bullish only).

A bullish reversal at the bottom of a downtrend: a long black candle, then a black candle
whose body sits inside the first's body yet whose low pierces below the first's low (the
"unique river"), then a small white candle opening above the second candle's low. TA-Lib's
``CDLUNIQUE3RIVER``::

    1st candle: black AND RealBody(1st) > BodyLong average(1st)        # long black
    2nd candle: black                                                 # black harami body
                AND open(2nd)  <= open(1st)                           # body within 1st (top)
                AND close(2nd) >  close(1st)                          # body within 1st (bottom)
                AND low(2nd)   <  low(1st)                            # but a new low — the river
    3rd candle: white AND RealBody(3rd) < BodyShort average(3rd)      # short white
                AND open(3rd)  >  low(2nd)                            # opens above the 2nd low

Note the second-body containment uses **open/close** with ``open(2nd) <= open(1st)`` (a tie on
the open passes) while the other edges are strict; there is no partial-penetration score, so
the output is only +100 (the pattern is bullish only) or 0 — never -100 and never the ±80
score.

``BodyLong`` and ``BodyShort`` are both ``(RealBody, 10, 1.0)`` with averaging period 10.
``BodyLong`` is read on the *first* candle (two bars back), so TA-Lib's lookback is
``max(10, 10) + 2 = 12`` (the first 12 bars are forced to 0).
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body

# TA-Lib reports a lookback of max(BodyLong, BodyShort) period + 2 = 10 + 2 = 12 for
# CDLUNIQUE3RIVER (the BodyLong average is read on the first of three bars).
_LOOKBACK = 12


def unique_three_river(df: pd.DataFrame) -> pd.Series:
    """Unique Three River pattern over ``df`` (OHLC) as a -100/0/100 ``Series`` (0 or +100).

    Matches ``talib.CDLUNIQUE3RIVER`` bit-exactly: +100 at the third bar of a Unique Three
    River formation (long black, then a black body inside the first with a lower low, then a
    short white opening above that low), 0 elsewhere. The output is pure 0/+100 (bullish only
    — no -100, no ±80 partial score). The first 12 bars are 0 (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    low = df[LOW].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    body_short = candle_average(df, "BodyShort").to_numpy()
    color = candle_color(df).to_numpy()
    n = len(c)
    out = np.zeros(n, dtype="float64")

    # Triplet (1st, 2nd, 3rd) = bars (i-2, i-1, i) for i in [2 .. n-1].
    first_black_long = (color[:-2] == -1) & (rb[:-2] > body_long[:-2])  # NaN average -> False
    second_black = color[1:-1] == -1
    body_within = (o[1:-1] <= o[:-2]) & (c[1:-1] > c[:-2])  # 2nd body inside 1st (<= on open)
    lower_low = low[1:-1] < low[:-2]  # 2nd makes a new low — the river
    third_white_short = (color[2:] == 1) & (rb[2:] < body_short[2:])  # NaN average -> False
    opens_above_low = o[2:] > low[1:-1]  # 3rd opens above the 2nd low

    hit = (
        first_black_long
        & second_black
        & body_within
        & lower_low
        & third_white_short
        & opens_above_low
    )
    out[2:] = np.where(hit, 100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 12 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class UniqueThreeRiver(Indicator):
    """Unique Three River candlestick pattern.

    What: a long black candle, then a black candle whose body sits inside the first but whose
        low pierces a new low, then a small white candle opening above that low — a bullish
        reversal hint at the bottom of a decline.
    Best settings: parameterless; the signal is bullish only (+100) or absent (0).
    Edge cases: the 2nd-body top edge test is ``open <= open`` (a tie passes) while the other
        edges are strict; first 12 bars are 0 (TA-Lib lookback = BodyLong period 10 on the
        first of three bars + 2).
    Parity: TA-Lib ``CDLUNIQUE3RIVER`` (BodyLong/BodyShort = RealBody/10/1.0), exact integer
        match — pure 0/+100, no ±80 partial-penetration score.
    """

    class Params(BaseModel):
        """Parameters for Unique Three River (TA-Lib ``CDLUNIQUE3RIVER`` takes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="unique_three_river",
        category="candles",
        aliases=("UniqueThreeRiver", "CDLUNIQUE3RIVER"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("unique_three_river",),
        bounds={"unique_three_river": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLUNIQUE3RIVER",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return unique_three_river(df)
