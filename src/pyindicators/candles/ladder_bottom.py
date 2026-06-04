"""CDLLADDERBOTTOM — Ladder Bottom pattern (five bars, bullish-only).

A bottom-reversal: three consecutive black candles step the market down, a fourth black
candle pauses the decline with an upper shadow (a failed intraday rally), and a fifth white
candle gaps up and closes above the fourth bar's high. TA-Lib::

    color(i-4) == -1 AND color(i-3) == -1 AND color(i-2) == -1   # three black candles
    open(i-4)  > open(i-3)  AND open(i-3)  > open(i-2)           # with lower opens
    close(i-4) > close(i-3) AND close(i-3) > close(i-2)          # and lower closes
    color(i-1) == -1 AND upper_shadow(i-1) > ShadowVeryShort avg(i-1)  # 4th black + upper shadow
    color(i)   ==  1                                             # 5th candle is white
    open(i)  > open(i-1)                                         # opening above the prior open
    close(i) > high(i-1)                                         # closing above the prior high

This is a one-sided (bullish) pattern: the output is **only +100 or 0** — there is no bearish
variant and no ±80 partial-penetration score. ``ShadowVeryShort`` is ``(HighLow, 10, 0.1)``;
with the extra four prior-bar offset, TA-Lib's lookback is 10 + 4 = 14 (the first 14 bars are
0). The first-three black bars carry no shadow/body-length requirement; the fifth bar's two
edge conditions (open > prior open AND close > prior high) are both strict ``>``.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, upper_shadow

# TA-Lib reports a lookback of 14 for CDLLADDERBOTTOM (ShadowVeryShort period 10 + 4 prior bars).
_LOOKBACK = 14


def ladder_bottom(df: pd.DataFrame) -> pd.Series:
    """Ladder Bottom over ``df`` (OHLC) as a 0/100 ``Series``.

    Matches ``talib.CDLLADDERBOTTOM`` bit-exactly: +100 where the five-bar bullish pattern
    forms, 0 elsewhere. The first 14 bars are 0 (TA-Lib lookback). Output is pure 0/+100 with
    no bearish variant and no ±80 partial-penetration score.
    """
    o = df[OPEN].to_numpy(dtype="float64")
    h = df[HIGH].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    color = candle_color(df).to_numpy()
    up = upper_shadow(df).to_numpy()
    svs = candle_average(df, "ShadowVeryShort").to_numpy()
    n = len(c)
    out = np.zeros(n, dtype="float64")

    if n > _LOOKBACK:
        # Current bar i runs over [4 .. n-1]; the three black candles are bars i-4, i-3, i-2.
        i = np.arange(4, n)
        i1 = i - 1
        i2 = i - 2
        i3 = i - 3
        i4 = i - 4

        hit = (
            (color[i4] == -1)
            & (color[i3] == -1)
            & (color[i2] == -1)
            & (o[i4] > o[i3])
            & (o[i3] > o[i2])
            & (c[i4] > c[i3])
            & (c[i3] > c[i2])
            & (color[i1] == -1)
            & (up[i1] > svs[i1])  # NaN ShadowVeryShort avg during warm-up -> False -> 0
            & (color[i] == 1)
            & (o[i] > o[i1])
            & (c[i] > h[i1])
        )
        out[4:] = np.where(hit, 100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 14 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class LadderBottom(Indicator):
    """Ladder Bottom candlestick pattern.

    What: three lower-stepping black candles, a fourth black candle with an upper shadow, then
    a white candle gapping up and closing above the prior high — a bullish bottom reversal.
    Best settings: parameterless; ``ShadowVeryShort`` body threshold is 10% of the 10-bar range.
    Edge cases: bullish-only (output is 0 or +100, never -100/±80); first 14 bars are 0.
    Parity: TA-Lib ``CDLLADDERBOTTOM`` (ShadowVeryShort = HighLow/10/0.1), exact integer match.
    """

    class Params(BaseModel):
        """Parameters for Ladder Bottom (TA-Lib ``CDLLADDERBOTTOM`` takes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="ladder_bottom",
        category="candles",
        aliases=("LadderBottom", "CDLLADDERBOTTOM"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("ladder_bottom",),
        bounds={"ladder_bottom": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLLADDERBOTTOM",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return ladder_bottom(df)
