"""CDLCONCEALBABYSWALL — Concealing Baby Swallow (four bars, bullish-only, magnitude 100).

A rare four-candle bullish reversal made of four **black** candles. TA-Lib::

    1st: black marubozu (short upper & lower shadows)
    2nd: black marubozu (short upper & lower shadows)
    3rd: black candle whose body gaps **down** below the 2nd body, yet whose long upper
         shadow trades back up *into* the 2nd body (high penetrates the 2nd close)
    4th: black candle that fully engulfs the 3rd's high-low range

Concretely the per-bar tests (``i`` = current 4th bar)::

    color(i-3)==-1 AND UpperShadow(i-3) < ShadowVeryShort AND LowerShadow(i-3) < ShadowVeryShort
    color(i-2)==-1 AND UpperShadow(i-2) < ShadowVeryShort AND LowerShadow(i-2) < ShadowVeryShort
    color(i-1)==-1 AND max(open,close)[i-1] < min(open,close)[i-2]      # body gaps down
                   AND UpperShadow(i-1) > ShadowVeryShort               # long upper shadow
                   AND high(i-1) > close(i-2)                           # shadow re-enters 2nd body
    color(i)  ==-1 AND high(i) > high(i-1) AND low(i) < low(i-1)        # engulfs the 3rd

Note (verified against ``talib`` on hand-built patterns + boundary-jitter fuzz): the 1st and
2nd "marubozu" are tested by their **shadows only** — TA-Lib does *not* require a long body for
them here, only short upper/lower shadows. Every edge comparison is strict (a tie scores 0).
Output is pure 0/100 (bullish only; no bearish or ±80 partial score).

``ShadowVeryShort`` is ``(HighLow, 10, 0.1)``. TA-Lib's lookback is ``10 + 3 = 13`` (the
ShadowVeryShort average of the earliest candle, ``i-3``, consumes 10 prior bars), so the first
13 bars are forced to 0.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, lower_shadow, upper_shadow

# TA-Lib reports a lookback of 13 for CDLCONCEALBABYSWALL: ShadowVeryShort period 10 on the
# earliest (i-3) candle, plus the three trailing bars the four-candle pattern spans.
_LOOKBACK = 13


def conceal_baby_swallow(df: pd.DataFrame) -> pd.Series:
    """Concealing Baby Swallow over ``df`` (OHLC) as a 0/100 ``Series``.

    Matches ``talib.CDLCONCEALBABYSWALL`` bit-exactly: four black candles where the first two
    are short-shadowed marubozu, the third gaps down in body but pokes a long upper shadow back
    into the second body, and the fourth engulfs the third's range. The first 13 bars are 0
    (TA-Lib lookback). Output is pure 0/100 — there is no bearish or partial ±80 score.
    """
    o = df[OPEN].to_numpy(dtype="float64")
    h = df[HIGH].to_numpy(dtype="float64")
    low = df[LOW].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    very_short = candle_average(df, "ShadowVeryShort").to_numpy()
    upsh = upper_shadow(df).to_numpy()
    losh = lower_shadow(df).to_numpy()
    color = candle_color(df).to_numpy()
    body_hi = np.maximum(o, c)
    body_lo = np.minimum(o, c)
    n = len(c)
    out = np.zeros(n, dtype="float64")

    if n > 3:
        # Align the four bars of the pattern: 1st=i-3, 2nd=i-2, 3rd=i-1, 4th=i.
        first = slice(0, n - 3)
        second = slice(1, n - 2)
        third = slice(2, n - 1)
        fourth = slice(3, n)

        # 1st & 2nd: black marubozu — short upper AND lower shadows (no body-length condition).
        first_maru = (
            (color[first] == -1)
            & (upsh[first] < very_short[first])  # NaN average -> False during warm-up
            & (losh[first] < very_short[first])
        )
        second_maru = (
            (color[second] == -1)
            & (upsh[second] < very_short[second])
            & (losh[second] < very_short[second])
        )
        # 3rd: black, body gaps down vs the 2nd, long upper shadow re-entering the 2nd body.
        third_ok = (
            (color[third] == -1)
            & (body_hi[third] < body_lo[second])
            & (upsh[third] > very_short[third])
            & (h[third] > c[second])
        )
        # 4th: black candle engulfing the 3rd's high-low range.
        fourth_ok = (color[fourth] == -1) & (h[fourth] > h[third]) & (low[fourth] < low[third])

        hit = first_maru & second_maru & third_ok & fourth_ok
        out[3:] = np.where(hit, 100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 13 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class ConcealBabySwallow(Indicator):
    """Concealing Baby Swallow candlestick pattern.

    What: a rare four-black-candle bullish reversal — two short-shadowed black marubozu, a third
    that gaps down but pokes a long upper shadow back into the second body, and a fourth that
    engulfs the third's range.
    Best settings: parameterless; bullish only (+100), driven by ShadowVeryShort = HighLow/10/0.1.
    Edge cases: pure 0/100 (no bearish or ±80 partial score); first 13 bars are 0 (TA-Lib
    lookback); every edge comparison is strict, so a tie scores 0.
    Parity: TA-Lib ``CDLCONCEALBABYSWALL`` (ShadowVeryShort = HighLow/10/0.1), exact integer match.
    """

    spec = IndicatorSpec(
        name="conceal_baby_swallow",
        category="candles",
        aliases=("Concealing Baby Swallow", "CDLCONCEALBABYSWALL"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("conceal_baby_swallow",),
        bounds={"conceal_baby_swallow": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLCONCEALBABYSWALL",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return conceal_baby_swallow(df)
