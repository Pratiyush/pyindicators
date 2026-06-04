"""CDLINNECK — In-Neck pattern (two bars, bearish continuation).

A long black candle is followed by a white candle that gaps down (opens below the prior low)
but rallies back only to close *just barely* into the prior black body — reaching no higher
than the prior close (plus a tiny Equal tolerance). The shallow penetration distinguishes
In-Neck (a bearish continuation) from the deeper Piercing pattern. TA-Lib::

    color(prev) == black                                  # 1st: long black candle
    AND RealBody(prev) > BodyLong average(prev)
    AND color(cur) == white                                # 2nd: white candle
    AND open(cur)  < low(prev)                             # gaps below the prior low
    AND close(cur) <= close(prev) + Equal average(prev)    # closes only just into the body
    AND close(cur) >= close(prev)                          # ... at or just above the prior close

Output is 0 or **-100** (purely bearish; no bullish or partial-penetration ±80 score — the
"reaching the prior close" test is itself an Equal tolerance band, not a strict edge tie).
This pattern takes **no** ``penetration`` parameter (unlike Dark Cloud / Piercing); the shallow
close is fixed by the ``Equal`` setting.

``BodyLong`` is ``(RealBody, 10, 1.0)`` and ``Equal`` is ``(HighLow, 5, 0.05)``. TA-Lib's
lookback is ``max(10, 5) + 1 = 11`` (the prior bar's BodyLong average needs 10 earlier bars),
so the first 11 bars are forced to 0.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body

# TA-Lib reports a lookback of 11 for CDLINNECK: max(BodyLong=10, Equal=5) + 1, the +1 coming
# from the previous-bar BodyLong/Equal averages (which themselves consume 10 earlier bars).
_LOOKBACK = 11


def in_neck(df: pd.DataFrame) -> pd.Series:
    """In-Neck pattern over ``df`` (OHLC) as a 0/-100 ``Series``.

    Matches ``talib.CDLINNECK`` bit-exactly: -100 where a long black candle is followed by a
    white candle that opens below the prior low yet closes only just into the prior body
    (at or barely above the prior close, within the Equal average), else 0. The first 11 bars
    are 0 (TA-Lib lookback). Output is pure 0/-100 — there is no partial ±80 score.
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
    # Closes only just into the prior body: at/above the prior close, no higher than the prior
    # close plus the Equal tolerance band.
    shallow = (c[1:] <= c[:-1] + equal[:-1]) & (c[1:] >= c[:-1])

    hit = black_long_prev & white_cur & gap_down & shallow
    out[1:] = np.where(hit, -100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 11 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class InNeck(Indicator):
    """In-Neck candlestick pattern.

    What: after a long black candle, a white candle gaps down but closes only just into the
    prior body (reaching the prior close) — a bearish continuation signal.
    Best settings: parameterless; the shallow penetration is fixed by the Equal setting (the
    close must sit between the prior close and prior close + Equal average).
    Edge cases: output is only 0 or -100 (no bullish/partial score); first 11 bars are 0.
    Parity: TA-Lib ``CDLINNECK`` (BodyLong = RealBody/10/1.0, Equal = HighLow/5/0.05), exact
    integer match.
    """

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="in_neck",
        category="candles",
        aliases=("InNeck", "CDLINNECK"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("in_neck",),
        bounds={"in_neck": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLINNECK",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    class Params(BaseModel):
        """Parameters for In-Neck (TA-Lib ``CDLINNECK`` takes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return in_neck(df)
