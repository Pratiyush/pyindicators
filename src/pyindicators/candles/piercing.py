"""CDLPIERCING — Piercing pattern (two bars, bullish reversal).

A long black candle is followed by a long white candle that opens *below the prior low* (a
gap down) and then closes back *up into* — but not above — the prior black body, finishing
above its midpoint. It is a bullish reversal signal. TA-Lib's exact test::

    CandleColor(prev) == -1                                  # 1st: black
    AND RealBody(prev) > BodyLong average(prev)              # 1st: long body
    AND CandleColor(cur)  == +1                              # 2nd: white
    AND RealBody(cur)  > BodyLong average(cur)               # 2nd: long body
    AND open[cur]  < low[prev]                               # opens below prior low (gap)
    AND close[cur] < open[prev]                              # closes within the prior body
    AND close[cur] > close[prev] + RealBody(prev) * 0.5      # above the prior midpoint

Output is a pure 0 or +100 — the pattern is single-signed (bullish only) and has no
partial-penetration ±80 score (the 0.5 midpoint pierce is hard-coded, and CDLPIERCING takes
no ``penetration`` parameter, unlike CDLDARKCLOUDCOVER).

``BodyLong`` is ``(RealBody, 10, 1.0)``; both candles' long-body averages need 10 prior bars,
so the average driving the previous bar needs bars ``[i-11 .. i-2]`` — TA-Lib's lookback is 11
(the first 11 bars are forced to 0).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body

# TA-Lib reports a lookback of 11 for CDLPIERCING (BodyLong period 10 on the previous bar).
_LOOKBACK = 11

# The pierce must clear the previous body's midpoint; TA-Lib hard-codes this 50% factor for
# CDLPIERCING (there is no ``penetration`` parameter, unlike CDLDARKCLOUDCOVER).
_MIDPOINT = 0.5


def piercing(df: pd.DataFrame) -> pd.Series:
    """Piercing pattern over ``df`` (OHLC) as a 0/100 ``Series`` (bullish-only).

    Matches ``talib.CDLPIERCING`` bit-exactly: +100 where the long-black / long-white pierce
    conditions all hold, 0 otherwise, and 0 during the 11-bar warm-up where the long-body
    average is undefined.
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    lo = df[LOW].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    color = candle_color(df).to_numpy()
    n = len(c)
    out = np.zeros(n, dtype="float64")

    # Previous = bars [0..n-2], current = bars [1..n-1].
    black_prev = color[:-1] == -1
    long_prev = rb[:-1] > body_long[:-1]  # NaN average -> False during warm-up
    white_cur = color[1:] == 1
    long_cur = rb[1:] > body_long[1:]
    gap_below = o[1:] < lo[:-1]
    within_prev = c[1:] < o[:-1]
    above_mid = c[1:] > c[:-1] + rb[:-1] * _MIDPOINT

    hit = black_prev & long_prev & white_cur & long_cur & gap_below & within_prev & above_mid
    out[1:] = np.where(hit, 100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 11 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class Piercing(Indicator):
    """Piercing candlestick pattern.

    What: a long white candle gaps below a prior long black candle's low, then closes back
    above its midpoint (but within its body) — a bullish reversal signal.
    Best settings: parameterless; the pierce threshold is the prior body's 50% midpoint.
    Edge cases: bullish-only (0 or +100, no ±80 partial score); first 11 bars are 0.
    Parity: TA-Lib ``CDLPIERCING`` (BodyLong = RealBody/10/1.0), exact integer match.
    """

    class Params(BaseModel):
        """No parameters: CDLPIERCING is fully determined (the 50% pierce is hard-coded)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec = IndicatorSpec(
        name="piercing",
        category="candles",
        aliases=("Piercing", "CDLPIERCING"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("piercing",),
        bounds={"piercing": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLPIERCING",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return piercing(df)
