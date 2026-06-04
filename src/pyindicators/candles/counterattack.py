"""CDLCOUNTERATTACK — Counterattack pattern (two bars, bidirectional).

Two long bodies of opposite colour whose **closes meet** — the second candle "counterattacks"
by closing right back at the first candle's close. TA-Lib::

    RealBody(prev) > BodyLong average(prev)          # first body is long
    AND RealBody(cur) > BodyLong average(cur)         # second body is long
    AND color(cur) == -color(prev)                    # opposite colours
    AND close(cur) <= close(prev) + Equal average(prev)
    AND close(cur) >= close(prev) - Equal average(prev)   # closes are ~equal

Sign is the current candle's colour (bullish = white now after a black candle). The output is a
pure ±100 / 0 signal — TA-Lib emits **no** ±80 partial-penetration score for this pattern (the
"close equality" is itself a tolerance band via the Equal setting, not a strict edge tie).

``BodyLong`` is ``(RealBody, 10, 1.0)`` and ``Equal`` is ``(HighLow, 5, 0.05)``. TA-Lib's
lookback is ``max(10, 5) + 1 = 11`` (the prior bar's BodyLong average needs 10 earlier bars),
so the first 11 bars are forced to 0.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body

# TA-Lib reports a lookback of 11 for CDLCOUNTERATTACK: max(BodyLong=10, Equal=5) + 1, the +1
# coming from the previous-bar BodyLong/Equal averages (which themselves consume 10 prior bars).
_LOOKBACK = 11


def counterattack(df: pd.DataFrame) -> pd.Series:
    """Counterattack pattern over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDLCOUNTERATTACK`` bit-exactly: two opposite-colour long bodies whose closes
    coincide (within the Equal average of the first bar). The first 11 bars are 0 (TA-Lib
    lookback). Output is pure ±100/0 — there is no partial ±80 score for this pattern.
    """
    c = df[CLOSE].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    equal = candle_average(df, "Equal").to_numpy()
    color = candle_color(df).to_numpy()
    n = len(c)
    out = np.zeros(n, dtype="float64")

    # Previous = bars [0..n-2], current = bars [1..n-1].
    long_prev = rb[:-1] > body_long[:-1]  # NaN average -> False during warm-up
    long_cur = rb[1:] > body_long[1:]
    opposite = color[1:] == -color[:-1]
    close_meets = (c[1:] <= c[:-1] + equal[:-1]) & (c[1:] >= c[:-1] - equal[:-1])

    hit = long_prev & long_cur & opposite & close_meets
    out[1:] = np.where(hit, color[1:] * 100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 11 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class Counterattack(Indicator):
    """Counterattack candlestick pattern.

    What: two opposite-colour long bodies whose closes meet — a reversal/indecision signal.
    Best settings: parameterless; bullish when a white candle follows a black one, bearish vice
    versa, provided both bodies are long and the closes are ~equal.
    Edge cases: pure ±100/0 (no ±80 partial score); first 11 bars are 0 (TA-Lib lookback).
    Parity: TA-Lib ``CDLCOUNTERATTACK`` (BodyLong = RealBody/10/1.0, Equal = HighLow/5/0.05),
    exact integer match.
    """

    spec = IndicatorSpec(
        name="counterattack",
        category="candles",
        aliases=("Counterattack", "CDLCOUNTERATTACK"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("counterattack",),
        bounds={"counterattack": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLCOUNTERATTACK",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return counterattack(df)
