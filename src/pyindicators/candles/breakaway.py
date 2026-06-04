"""CDLBREAKAWAY — Breakaway pattern (five bars, bidirectional).

A five-candle reversal that "breaks away" from an accelerating trend and then snaps back
into the gap that launched it. TA-Lib's test (mirror image for the two directions)::

    color(1st) == color(2nd) == color(4th) == -color(5th)   # 1st/2nd/4th agree, 5th opposite
    RealBody(1st) > BodyLong average(1st)                    # 1st is a long candle

    bearish-structure (1st..4th black), 5th white  -> +100:
        body(2nd) gaps DOWN below body(1st)
        high(3rd) < high(2nd) and low(3rd) < low(2nd)       # 3rd continues lower
        high(4th) < high(3rd) and low(4th) < low(3rd)       # 4th continues lower
        close(5th) > open(2nd) and close(5th) < close(1st)  # 5th closes back inside the gap

    bullish-structure (1st..4th white), 5th black  -> -100:
        body(2nd) gaps UP above body(1st)
        high(3rd) > high(2nd) and low(3rd) > low(2nd)
        high(4th) > high(3rd) and low(4th) > low(3rd)
        close(5th) < open(2nd) and close(5th) > close(1st)

The sign TA-Lib emits is the **5th** candle's colour (``candle_color(i) * 100``), so the
"bullish-structure" gap-up variant scores -100 and the "bearish-structure" gap-down variant
scores +100. Output is strictly -100/0/100 — this pattern has no partial-penetration ±80
score (every comparison is a strict inequality, no body-edge tie produces a partial hit).

``BodyLong`` is ``(RealBody, 10, 1.0)``; its average for the 1st candle uses the 10 bars
ending one before it, and the pattern itself spans 4 prior bars, so TA-Lib's lookback is
``10 + 4 = 14`` — the first 14 bars are forced to 0.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body

# TA-Lib reports a lookback of 14 for CDLBREAKAWAY (BodyLong period 10 + 4 prior bars).
_LOOKBACK = 14


def breakaway(df: pd.DataFrame) -> pd.Series:
    """Breakaway pattern over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDLBREAKAWAY`` bit-exactly. The sign is the fifth (final) candle's colour;
    the first 14 bars are 0 (TA-Lib lookback). No ±80 partial score for this pattern.
    """
    o = df[OPEN].to_numpy(dtype="float64")
    h = df[HIGH].to_numpy(dtype="float64")
    low = df[LOW].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    color = candle_color(df).to_numpy()
    rb = real_body(df).to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    body_hi = np.maximum(o, c)
    body_lo = np.minimum(o, c)

    n = len(c)
    out = np.zeros(n, dtype="float64")
    if n <= _LOOKBACK:
        return pd.Series(out, index=df.index)

    # Align the five candles: index i is the 5th candle, i-4 the 1st (windowed from _LOOKBACK).
    i = np.arange(_LOOKBACK, n)
    c1, c2, c3, c4, c5 = i - 4, i - 3, i - 2, i - 1, i

    # Colour agreement: 1st == 2nd == 4th, and 5th is the opposite colour.
    same_color = (
        (color[c1] == color[c2]) & (color[c2] == color[c4]) & (color[c4] == -color[c5])
    )
    long_first = rb[c1] > body_long[c1]  # NaN average during warm-up -> False (excluded anyway)

    # Bearish structure (1st..4th black): gap down, two lower bars, 5th closes inside the gap.
    black = color[c1] == -1
    gap_down = body_hi[c2] < body_lo[c1]
    lower_3 = (h[c3] < h[c2]) & (low[c3] < low[c2])
    lower_4 = (h[c4] < h[c3]) & (low[c4] < low[c3])
    close_in_down = (c[c5] > o[c2]) & (c[c5] < c[c1])
    bear = black & gap_down & lower_3 & lower_4 & close_in_down

    # Bullish structure (1st..4th white): gap up, two higher bars, 5th closes inside the gap.
    white = color[c1] == 1
    gap_up = body_lo[c2] > body_hi[c1]
    higher_3 = (h[c3] > h[c2]) & (low[c3] > low[c2])
    higher_4 = (h[c4] > h[c3]) & (low[c4] > low[c3])
    close_in_up = (c[c5] < o[c2]) & (c[c5] > c[c1])
    bull = white & gap_up & higher_3 & higher_4 & close_in_up

    hit = same_color & long_first & (bear | bull)
    out[_LOOKBACK:] = np.where(hit, color[c5] * 100.0, 0.0)
    return pd.Series(out, index=df.index)


@INDICATORS.register
class Breakaway(Indicator):
    """Breakaway candlestick pattern.

    What: a five-bar reversal that gaps away from an accelerating trend, then closes back
    inside the launching gap on the fifth bar.
    Best settings: parameterless; the first candle must be long (> 10-bar average body).
    Edge cases: first 14 bars are 0; sign is the fifth candle's colour, so a gap-up
    (white-tendency) breakaway scores -100 and a gap-down (black-tendency) one scores +100.
    Parity: TA-Lib ``CDLBREAKAWAY`` (BodyLong = RealBody/10/1.0), exact integer match (no ±80).
    """

    class Params(BaseModel):
        """Breakaway takes no parameters (TA-Lib ``CDLBREAKAWAY`` has none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec = IndicatorSpec(
        name="breakaway",
        category="candles",
        aliases=("Breakaway", "CDLBREAKAWAY"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("breakaway",),
        bounds={"breakaway": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLBREAKAWAY",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return breakaway(df)
