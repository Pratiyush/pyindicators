"""CDL3STARSINSOUTH — Three Stars In The South (three bars, bullish reversal).

A rare bottoming pattern: three consecutive black candles that shrink and tighten as selling
pressure fades. TA-Lib's exact test (``i`` is the third/current bar)::

    1st (i-2): black, long real body with a long lower shadow
        RealBody(i-2)    > BodyLong   average(i-2)
        LowerShadow(i-2) > ShadowLong average(i-2)   # ShadowLong = RealBody/0/1 -> RealBody(i-2)
    2nd (i-1): black, smaller body that opens higher into the 1st range and makes a higher low,
               but still has a lower shadow
        RealBody(i-1) < RealBody(i-2)
        open(i-1) >  close(i-2)  AND  open(i-1) <= high(i-2)
        low(i-1)  <  close(i-2)  AND  low(i-1)  >= low(i-2)
        LowerShadow(i-1) > ShadowVeryShort average(i-1)
    3rd (i): black small marubozu engulfed by the 2nd bar's range
        RealBody(i)    < BodyShort        average(i)
        LowerShadow(i) < ShadowVeryShort  average(i)
        UpperShadow(i) < ShadowVeryShort  average(i)
        low(i) > low(i-1)  AND  high(i) < high(i-1)

``BodyLong``/``BodyShort`` are ``(RealBody, 10, 1.0)``; ``ShadowLong`` is ``(RealBody, 0, 1.0)``
(so its threshold is the bar's own real body); ``ShadowVeryShort`` is ``(HighLow, 10, 0.1)``.
The output is 0 or +100 (the pattern is single-signed, bullish — never negative and never the
±80 partial-penetration score, as none of its comparisons are body-edge ties).

The longest averaging period is ``BodyLong``/``BodyShort`` = 10 and the pattern spans three
bars, so TA-Lib's lookback is ``10 + 2 = 12``; the first 12 bars are forced to 0.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, lower_shadow, real_body, upper_shadow

# TA-Lib lookback: max avg period (BodyLong/BodyShort = 10) plus the two prior bars = 12.
_LOOKBACK = 12


def three_stars_in_south(df: pd.DataFrame) -> pd.Series:
    """Three Stars In The South over ``df`` (OHLC) as a -100/0/100 ``Series`` (here 0 or 100).

    Matches ``talib.CDL3STARSINSOUTH`` bit-exactly: +100 where the three-bar bullish pattern
    forms, 0 elsewhere. The first 12 bars are 0 (TA-Lib lookback); the output is pure 0/+100
    (single-signed, no ±80 partial-penetration score).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    h = df[HIGH].to_numpy(dtype="float64")
    low = df[LOW].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")

    rb = real_body(df).to_numpy()
    us = upper_shadow(df).to_numpy()
    ls = lower_shadow(df).to_numpy()
    color = candle_color(df).to_numpy()

    body_long = candle_average(df, "BodyLong").to_numpy()
    body_short = candle_average(df, "BodyShort").to_numpy()
    shadow_long = candle_average(df, "ShadowLong").to_numpy()  # = RealBody (period 0)
    very_short = candle_average(df, "ShadowVeryShort").to_numpy()

    n = len(o)
    out = np.zeros(n, dtype="float64")
    if n <= _LOOKBACK:
        return pd.Series(out, index=df.index)

    # Align the three bars: prev2 = [.. i-2], prev1 = [.. i-1], cur = [.. i]. NaN warm-up
    # averages make their comparisons False, so the lookback region stays 0 regardless.
    c2 = color[:-2]
    c1 = color[1:-1]
    c0 = color[2:]

    # 1st candle (i-2): black, long body, long lower shadow.
    first = (c2 == -1) & (rb[:-2] > body_long[:-2]) & (ls[:-2] > shadow_long[:-2])

    # 2nd candle (i-1): black, smaller body, opens into the 1st range with a higher low and a
    # lower shadow.
    second = (
        (c1 == -1)
        & (rb[1:-1] < rb[:-2])
        & (o[1:-1] > c[:-2])
        & (o[1:-1] <= h[:-2])
        & (low[1:-1] < c[:-2])
        & (low[1:-1] >= low[:-2])
        & (ls[1:-1] > very_short[1:-1])
    )

    # 3rd candle (i): black small marubozu engulfed by the 2nd bar's range.
    third = (
        (c0 == -1)
        & (rb[2:] < body_short[2:])
        & (ls[2:] < very_short[2:])
        & (us[2:] < very_short[2:])
        & (low[2:] > low[1:-1])
        & (h[2:] < h[1:-1])
    )

    out[2:] = np.where(first & second & third, 100.0, 0.0)
    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 12 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class ThreeStarsInSouth(Indicator):
    """Three Stars In The South candlestick pattern.

    What: three shrinking black candles at a bottom — selling pressure exhausts into a bullish
    reversal. Each bar is black; the body and range tighten from the long first candle to the
    small engulfed third.
    Best settings: parameterless; long first body/shadow (10-bar averages), short third body.
    Edge cases: first 12 bars are 0 (TA-Lib lookback); output is pure 0/+100 (no sign, no ±80).
    Parity: TA-Lib ``CDL3STARSINSOUTH`` (BodyLong/BodyShort = RealBody/10/1.0, ShadowLong =
    RealBody/0/1.0, ShadowVeryShort = HighLow/10/0.1), exact integer match.
    """

    class Params(BaseModel):
        """Parameters for Three Stars In The South (TA-Lib ``CDL3STARSINSOUTH`` takes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="three_stars_in_south",
        category="candles",
        aliases=("ThreeStarsInSouth", "CDL3STARSINSOUTH"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("three_stars_in_south",),
        bounds={"three_stars_in_south": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDL3STARSINSOUTH",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return three_stars_in_south(df)
