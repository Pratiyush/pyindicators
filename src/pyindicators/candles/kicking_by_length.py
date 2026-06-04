"""CDLKICKINGBYLENGTH — Kicking, bull/bear by the longer marubozu (two bars, bidirectional).

Two opposite-colour marubozu candles separated by a price gap. A *marubozu* here is a long
real body with negligible (very-short) upper **and** lower shadows. TA-Lib::

    color(prev) == -color(cur)                                   # opposite colours
    AND RealBody(prev) > BodyLong  average(prev)                 # both are long bodies
    AND RealBody(cur)  > BodyLong  average(cur)
    AND UpperShadow(prev) < ShadowVeryShort average(prev)        # both are marubozu
    AND LowerShadow(prev) < ShadowVeryShort average(prev)        #   (tiny shadows)
    AND UpperShadow(cur)  < ShadowVeryShort average(cur)
    AND LowerShadow(cur)  < ShadowVeryShort average(cur)
    AND (  (color(prev) == -1 AND low(cur)  > high(prev))        # black then gap-up
        OR (color(prev) == +1 AND high(cur) < low(prev)) )       # white then gap-down

The sign is the colour of whichever candle has the **longer** real body (this is the only
difference from plain ``CDLKICKING``, which always uses the *current* candle's colour); the
magnitude is always 100 (no partial-penetration score). Both ``BodyLong`` and
``ShadowVeryShort`` average over the 10 bars ending at the bar being tested, so TA-Lib's
lookback is ``max(10, 10) + 1 = 11`` (the first 11 bars are 0).

Takes no parameters (TA-Lib ``CDLKICKINGBYLENGTH`` has no ``penetration`` factor).
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, lower_shadow, real_body, upper_shadow

# TA-Lib lookback = max(BodyLong, ShadowVeryShort avgPeriod) + 1 = max(10, 10) + 1.
_LOOKBACK = 11


def kicking_by_length(df: pd.DataFrame) -> pd.Series:
    """Kicking-by-length pattern over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDLKICKINGBYLENGTH`` bit-exactly: two opposite-colour marubozu candles
    with a gap between them, signed by the longer marubozu's colour. The first 11 bars are 0
    (TA-Lib lookback); the magnitude is always 100 (no ±80 partial score for this pattern).
    """
    high = df[HIGH].to_numpy(dtype="float64")
    low = df[LOW].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    upper = upper_shadow(df).to_numpy()
    lower = lower_shadow(df).to_numpy()
    color = candle_color(df).to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    shadow_vs = candle_average(df, "ShadowVeryShort").to_numpy()
    n = len(rb)
    out = np.zeros(n, dtype="float64")

    if n > 1:
        # Previous = bars [0..n-2], current = bars [1..n-1]; NaN averages -> False.
        opposite = color[:-1] == -color[1:]
        prev_marubozu = (
            (rb[:-1] > body_long[:-1])
            & (upper[:-1] < shadow_vs[:-1])
            & (lower[:-1] < shadow_vs[:-1])
        )
        cur_marubozu = (
            (rb[1:] > body_long[1:])
            & (upper[1:] < shadow_vs[1:])
            & (lower[1:] < shadow_vs[1:])
        )
        gap = ((color[:-1] == -1) & (low[1:] > high[:-1])) | (
            (color[:-1] == 1) & (high[1:] < low[:-1])
        )
        hit = opposite & prev_marubozu & cur_marubozu & gap

        # Sign = colour of the candle with the longer real body (current if strictly longer).
        cur_longer = rb[1:] > rb[:-1]
        sign = np.where(cur_longer, color[1:], color[:-1])
        out[1:] = np.where(hit, sign * 100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 11 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class KickingByLength(Indicator):
    """Kicking (by length) candlestick pattern.

    What: two opposite-colour marubozu candles with a gap between them — a strong reversal;
    the signal's direction is set by whichever marubozu has the longer body.
    Best settings: parameterless; bullish when a black marubozu gaps up into a white one.
    Edge cases: magnitude is always 100 (no ±80 partial score); first 11 bars are 0.
    Parity: TA-Lib ``CDLKICKINGBYLENGTH`` (BodyLong + ShadowVeryShort marubozu test), exact.
    """

    class Params(BaseModel):
        """No parameters: ``CDLKICKINGBYLENGTH`` takes no ``penetration`` factor."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="kicking_by_length",
        category="candles",
        aliases=("KickingByLength", "CDLKICKINGBYLENGTH"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("kicking_by_length",),
        bounds={"kicking_by_length": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLKICKINGBYLENGTH",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return kicking_by_length(df)
