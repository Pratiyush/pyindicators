"""CDLMORNINGDOJISTAR — Morning Doji Star (three bars, bullish reversal).

A downtrend's long black candle is followed by a doji that gaps *down* away from it (the star),
then a white candle that closes deep back into the first black body — a bullish bottom-reversal
whose middle star is specifically a doji. TA-Lib::

    RealBody(1st) > BodyLong  average(1st)   AND color(1st) == black   # long black candle
    AND RealBody(2nd) <= BodyDoji average(2nd)                         # 2nd is a doji
    AND realBodyGapDown(2nd, 1st)                                      # doji gaps down under 1st
    AND RealBody(3rd) > BodyShort average(3rd) AND color(3rd) == white # 3rd is a white body
    AND close(3rd) > close(1st) + RealBody(1st) * penetration         # deep into the 1st body

where the real-body gap down is strict — ``max(open, close)[2nd] < min(open, close)[1st]``. Note
TA-Lib requires a gap down before the star but **no** gap up after it (the third candle need not
gap away from the doji). Output is 0 or **+100** (purely bullish; no bearish or ±80
partial-penetration score). The ``penetration`` factor defaults to TA-Lib's 0.3 (how far above
the 1st close the white candle must close, as a fraction of the 1st real body).

This is the bullish mirror of :mod:`evening_doji_star`.

``BodyLong``/``BodyShort`` are ``(RealBody, 10, 1.0)`` and ``BodyDoji`` is ``(HighLow, 10, 0.1)``.
TA-Lib's lookback is ``max(10, 10, 10) + 2 = 12`` (the averages need 10 bars ending at the bar
before each candle, and the pattern spans three bars), so the first 12 bars are forced to 0.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body

# TA-Lib reports a lookback of max(BodyDoji, BodyLong, BodyShort) + 2 = 12 for CDLMORNINGDOJISTAR.
_LOOKBACK = 12

# TA-Lib's default penetration for CDLMORNINGDOJISTAR.
_DEFAULT_PENETRATION = 0.3


def morning_doji_star(df: pd.DataFrame, penetration: float = _DEFAULT_PENETRATION) -> pd.Series:
    """Morning Doji Star over ``df`` (OHLC) as a 0/100 ``Series``.

    Matches ``talib.CDLMORNINGDOJISTAR`` bit-exactly: 100 where a long black candle is followed
    by a doji that gaps down, then a white candle that closes more than ``penetration`` of the
    first body above the first close, else 0. The first 12 bars are 0 (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    body_doji = candle_average(df, "BodyDoji").to_numpy()
    body_short = candle_average(df, "BodyShort").to_numpy()
    body_hi = np.maximum(o, c)
    body_lo = np.minimum(o, c)
    color = candle_color(df).to_numpy()
    n = len(c)
    out = np.zeros(n, dtype="float64")

    if n > _LOOKBACK:
        # 1st = bars [0..n-3], 2nd = bars [1..n-2], 3rd (current) = bars [2..n-1].
        first = slice(0, n - 2)
        second = slice(1, n - 1)
        third = slice(2, n)

        long_black_1 = (rb[first] > body_long[first]) & (color[first] == -1)  # NaN avg -> False
        doji_2 = rb[second] <= body_doji[second]
        gap_down_2 = body_hi[second] < body_lo[first]  # strict real-body gap down under the 1st
        white_3 = (rb[third] > body_short[third]) & (color[third] == 1)
        deep_3 = c[third] > c[first] + rb[first] * penetration

        hit = long_black_1 & doji_2 & gap_down_2 & white_3 & deep_3
        out[2:] = np.where(hit, 100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 12 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class MorningDojiStar(Indicator):
    """Morning Doji Star candlestick pattern.

    What: a long black candle, then a gapped-down doji star, then a white candle that closes deep
    into the first body — a bullish bottom-reversal (the mirror of the Evening Doji Star).
    Best settings: ``penetration`` (default 0.3) sets how far above the first close the white
    candle must close, as a fraction of the first real body.
    Edge cases: the gap down before the star is strict (no gap up required after it); output is
    only 0 or +100 (no bearish/partial score); first 12 bars are 0.
    Parity: TA-Lib ``CDLMORNINGDOJISTAR`` (BodyLong/BodyShort = RealBody/10/1.0,
    BodyDoji = HighLow/10/0.1, penetration 0.3), exact.
    """

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="morning_doji_star",
        category="candles",
        aliases=("MorningDojiStar", "CDLMORNINGDOJISTAR"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("morning_doji_star",),
        bounds={"morning_doji_star": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLMORNINGDOJISTAR",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        penetration: float = Field(
            default=_DEFAULT_PENETRATION,
            ge=0.0,
            description="Fraction of the first real body the white candle must close above "
            "the first close (TA-Lib default 0.3).",
        )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return morning_doji_star(df, penetration=self.params["penetration"])
