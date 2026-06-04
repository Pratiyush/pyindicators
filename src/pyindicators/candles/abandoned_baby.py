"""CDLABANDONEDBABY — Abandoned Baby (three bars, bidirectional, gapped doji).

A long candle, then a doji **isolated by gaps on both sides** (an "abandoned baby"), then a
long candle of the opposite colour that closes well back into the first candle's body. TA-Lib::

    bullish (+100): black long #1, doji #2 gapped *below* #1, white long #3 gapped *above* #2,
                    close[i] > close[i-2] + RealBody(i-2) * penetration   (deep into #1's body)
    bearish (-100): white long #1, doji #2 gapped *above* #1, black long #3 gapped *below* #2,
                    close[i] < close[i-2] - RealBody(i-2) * penetration

where the gaps use the full ``high``/``low`` (not the bodies): a downside gap is
``high[i-1] < low[i-2]`` and an upside gap is ``low[i] > high[i-1]`` (both strict). #1 and #3
must be "long" (``RealBody > BodyLong`` average) and #2 must be a doji
(``RealBody <= BodyDoji`` average). Output is a clean ±100 / 0 — there is no partial score.

``BodyLong`` is ``(RealBody, 10, 1.0)`` and ``BodyDoji`` is ``(HighLow, 10, 0.1)``; the longest
average period is 10 and the pattern spans 2 prior bars, so TA-Lib's lookback is 12 (the first
12 bars are forced to 0). ``penetration`` defaults to 0.3 (TA-Lib's default).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body

# TA-Lib reports a lookback of 12 for CDLABANDONEDBABY (BodyDoji/BodyLong period 10 + 2 bars).
_LOOKBACK = 12
_DEFAULT_PENETRATION = 0.3


def abandoned_baby(df: pd.DataFrame, penetration: float = _DEFAULT_PENETRATION) -> pd.Series:
    """Abandoned Baby over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDLABANDONEDBABY`` bit-exactly. The first 12 bars are 0 (TA-Lib lookback).
    """
    h = df[HIGH].to_numpy(dtype="float64")
    low = df[LOW].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    body_doji = candle_average(df, "BodyDoji").to_numpy()
    color = candle_color(df).to_numpy()
    n = len(c)
    out = np.zeros(n, dtype="float64")

    # Index alignment: #1 = i-2 = [..:-2], #2 = i-1 = [1:-1], #3 = i = [2:].
    c1_color = color[:-2]
    c1_long = rb[:-2] > body_long[:-2]
    c1_close = c[:-2]
    c1_rb = rb[:-2]
    c1_low = low[:-2]
    c1_high = h[:-2]

    c2_doji = rb[1:-1] <= body_doji[1:-1]
    c2_low = low[1:-1]
    c2_high = h[1:-1]

    c3_color = color[2:]
    c3_long = rb[2:] > body_long[2:]
    c3_close = c[2:]
    c3_low = low[2:]
    c3_high = h[2:]

    # Bullish: black #1, doji #2 gapped down, white #3 gapped up closing deep into #1's body.
    gap_down = c2_high < c1_low  # downside gap #1 -> #2 (full high/low)
    gap_up = c3_low > c2_high  # upside gap #2 -> #3
    bull = (
        (c1_color == -1)
        & c1_long
        & c2_doji
        & (c3_color == 1)
        & c3_long
        & gap_down
        & gap_up
        & (c3_close > c1_close + c1_rb * penetration)
    )

    # Bearish: white #1, doji #2 gapped up, black #3 gapped down closing deep into #1's body.
    gap_up_12 = c2_low > c1_high  # upside gap #1 -> #2
    gap_down_23 = c3_high < c2_low  # downside gap #2 -> #3
    bear = (
        (c1_color == 1)
        & c1_long
        & c2_doji
        & (c3_color == -1)
        & c3_long
        & gap_up_12
        & gap_down_23
        & (c3_close < c1_close - c1_rb * penetration)
    )

    body = np.zeros(max(0, n - 2), dtype="float64")  # max() guards frames shorter than 3 bars
    body[bull] = 100.0
    body[bear] = -100.0
    out[2:] = body

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 12 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class AbandonedBaby(Indicator):
    """Abandoned Baby candlestick pattern.

    What: a doji isolated by gaps on both sides between two long opposite-colour bodies, the
    third closing deep into the first — a strong reversal signal.
    Best settings: ``penetration`` 0.3 (TA-Lib default); bullish off a black #1, bearish off a
    white #1.
    Edge cases: gaps use full high/low (strict); #1 and #3 must be long, #2 a doji; first 12
    bars are 0.
    Parity: TA-Lib ``CDLABANDONEDBABY`` (BodyLong/BodyDoji, penetration 0.3), exact integer.
    """

    spec = IndicatorSpec(
        name="abandoned_baby",
        category="candles",
        aliases=("Abandoned Baby", "CDLABANDONEDBABY"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("abandoned_baby",),
        bounds={"abandoned_baby": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLABANDONEDBABY",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        penetration: float = Field(default=_DEFAULT_PENETRATION, ge=0.0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return abandoned_baby(df, self.params["penetration"])
