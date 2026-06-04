"""CDLTHRUSTING — Thrusting pattern (two bars, bearish continuation).

A long black candle is followed by a white candle that gaps down (opens below the prior low)
and rallies back *into* the prior black body — closing well above the prior close, yet not as
far as the prior body's midpoint. The penetration is deeper than In-Neck (which closes only
just at the prior close) but shallower than Piercing (which clears the midpoint, turning the
signal bullish). It is a bearish continuation signal. TA-Lib's exact test::

    color(prev) == black                                  # 1st: long black candle
    AND RealBody(prev) > BodyLong average(prev)
    AND color(cur) == white                                # 2nd: white candle
    AND open(cur)  < low(prev)                             # gaps below the prior low
    AND close(cur) > close(prev) + Equal average(prev)     # closes well into the body ...
    AND close(cur) <= close(prev) + RealBody(prev) * 0.5   # ... but not past the midpoint

Output is 0 or **-100** (purely bearish; no bullish or partial-penetration ±80 score — both
penetration edges are tolerance/midpoint bands, not strict body-edge ties). This pattern takes
**no** ``penetration`` parameter (unlike Dark Cloud / Piercing; verified via the empty TA-Lib
parameter list); the shallow lower band is fixed by the ``Equal`` setting and the upper band by
the hard-coded 50% midpoint.

``BodyLong`` is ``(RealBody, 10, 1.0)`` and ``Equal`` is ``(HighLow, 5, 0.05)``. TA-Lib's
lookback is ``max(10, 5) + 1 = 11`` (the prior bar's BodyLong/Equal averages each consume 10
earlier bars), so the first 11 bars are forced to 0.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body

# TA-Lib reports a lookback of 11 for CDLTHRUSTING: max(BodyLong=10, Equal=5) + 1, the +1 coming
# from the previous-bar BodyLong/Equal averages (which themselves consume 10 earlier bars).
_LOOKBACK = 11

# The close must reach into the prior body but stop at or below its midpoint; TA-Lib hard-codes
# this 50% factor for CDLTHRUSTING (there is no ``penetration`` parameter, unlike Dark Cloud).
_MIDPOINT = 0.5


def thrusting(df: pd.DataFrame) -> pd.Series:
    """Thrusting pattern over ``df`` (OHLC) as a 0/-100 ``Series``.

    Matches ``talib.CDLTHRUSTING`` bit-exactly: -100 where a long black candle is followed by a
    white candle that opens below the prior low and closes well into the prior body (above the
    prior close by more than the Equal average) yet no higher than the prior body's midpoint,
    else 0. The first 11 bars are 0 (TA-Lib lookback). Output is pure 0/-100 — there is no
    partial ±80 score.
    """
    o = df[OPEN].to_numpy(dtype="float64")
    low = df[LOW].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    equal = candle_average(df, "Equal").to_numpy()
    color = candle_color(df).to_numpy()
    n = len(c)
    out = np.zeros(n, dtype="float64")

    # Previous = bars [0..n-2], current = bars [1..n-1].
    black_long_prev = (color[:-1] == -1) & (rb[:-1] > body_long[:-1])  # NaN average -> False
    white_cur = color[1:] == 1
    gap_down = o[1:] < low[:-1]
    # Closes well into the prior body: above the prior close by more than the Equal tolerance
    # (deeper than In-Neck), but no higher than the prior body's midpoint (shallower than a
    # bullish Piercing).
    lower = c[1:] > c[:-1] + equal[:-1]
    upper = c[1:] <= c[:-1] + rb[:-1] * _MIDPOINT

    hit = black_long_prev & white_cur & gap_down & lower & upper
    out[1:] = np.where(hit, -100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 11 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class Thrusting(Indicator):
    """Thrusting candlestick pattern.

    What: after a long black candle, a white candle gaps down but closes well into the prior
    body without clearing its midpoint — a bearish continuation signal.
    Best settings: parameterless; the close must sit above the prior close by more than the
    Equal average yet at or below the prior body's 50% midpoint.
    Edge cases: output is only 0 or -100 (no bullish/partial score); first 11 bars are 0.
    Parity: TA-Lib ``CDLTHRUSTING`` (BodyLong = RealBody/10/1.0, Equal = HighLow/5/0.05), exact
    integer match.
    """

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="thrusting",
        category="candles",
        aliases=("Thrusting", "CDLTHRUSTING"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("thrusting",),
        bounds={"thrusting": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLTHRUSTING",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    class Params(BaseModel):
        """Parameters for Thrusting (TA-Lib ``CDLTHRUSTING`` takes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return thrusting(df)
