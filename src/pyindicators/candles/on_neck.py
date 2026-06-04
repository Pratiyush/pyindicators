"""CDLONNECK — On-Neck pattern (two bars, bearish continuation).

A long black candle is followed by a small white candle that gaps down at the open but rallies
only back up to (roughly) the *low* of the prior black body — the buyers fail to penetrate the
prior bar, so the downtrend is expected to continue. TA-Lib's test::

    CandleColor(prev) == -1                                  # 1st: black
    AND RealBody(prev) > BodyLong average(prev)              # ...long body
    AND CandleColor(cur)  == +1                              # 2nd: white
    AND open(cur)  < low(prev)                               # gaps below the prior low
    AND close(cur) >= low(prev) - Equal average(prev)        # closes *at* the prior low
    AND close(cur) <= low(prev) + Equal average(prev)        # (within the Equal band)

Both ``Equal`` and ``BodyLong`` averages are evaluated on the **previous** bar. There is no
partial-penetration score here: the output is a pure bearish -100 (or 0), never ±80.

``BodyLong`` is ``(RealBody, 10, 1.0)`` and ``Equal`` is ``(HighLow, 5, 0.05)``; both are read
on the prior bar, so TA-Lib's lookback is ``max(10, 5) + 1 = 11`` (the first 11 bars are 0).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body

# TA-Lib lookback for CDLONNECK: max(BodyLong avgPeriod=10, Equal avgPeriod=5) + 1 = 11.
_LOOKBACK = 11


def on_neck(df: pd.DataFrame) -> pd.Series:
    """On-Neck pattern over ``df`` (OHLC) as a -100/0 ``Series``.

    Matches ``talib.CDLONNECK`` bit-exactly: -100 on a long black bar followed by a white bar
    that gaps down and closes back at the prior low (within the ``Equal`` band), 0 otherwise.
    The first 11 bars are 0 (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    low = df[LOW].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    equal = candle_average(df, "Equal").to_numpy()
    color = candle_color(df).to_numpy()
    n = len(c)
    out = np.zeros(n, dtype="float64")

    # Previous = bars [0..n-2], current = bars [1..n-1]; averages read on the previous bar.
    prev_black = color[:-1] == -1
    long_prev = rb[:-1] > body_long[:-1]  # NaN average -> False during warm-up
    cur_white = color[1:] == 1
    open_below = o[1:] < low[:-1]
    eq_prev = equal[:-1]
    close_near = (c[1:] >= low[:-1] - eq_prev) & (c[1:] <= low[:-1] + eq_prev)

    hit = prev_black & long_prev & cur_white & open_below & close_near
    out[1:] = np.where(hit, -100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 11 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class OnNeck(Indicator):
    """On-Neck candlestick pattern.

    What: a long black bar then a white bar that gaps down but only rallies to the prior low —
    a bearish continuation signal.
    Best settings: parameterless; the close must land within the ``Equal`` band of the prior low.
    Edge cases: bearish-only (-100 or 0, never ±80); first 11 bars are 0.
    Parity: TA-Lib ``CDLONNECK`` (BodyLong = RealBody/10/1.0, Equal = HighLow/5/0.05), exact.
    """

    spec = IndicatorSpec(
        name="on_neck",
        category="candles",
        aliases=("OnNeck", "CDLONNECK"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("on_neck",),
        bounds={"on_neck": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLONNECK",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return on_neck(df)
