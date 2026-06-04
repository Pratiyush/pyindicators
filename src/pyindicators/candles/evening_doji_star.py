"""CDLEVENINGDOJISTAR — Evening Doji Star (three bars, bearish reversal).

An uptrend's long white candle is followed by a doji that gaps *up* away from it (the star),
then a black candle that closes deep back into the first white body — a bearish top-reversal
whose middle star is specifically a doji. TA-Lib::

    RealBody(1st) > BodyLong  average(1st)   AND color(1st) == white   # long white candle
    AND RealBody(2nd) <= BodyDoji average(2nd)                         # 2nd is a doji
    AND realBodyGapUp(2nd, 1st)                                        # doji gaps up over 1st
    AND RealBody(3rd) > BodyShort average(3rd) AND color(3rd) == black # 3rd is a black body
    AND close(3rd) < close(1st) - RealBody(1st) * penetration         # deep into the 1st body

where the real-body gap up is strict — ``min(open, close)[2nd] > max(open, close)[1st]``. Note
TA-Lib requires a gap up before the star but **no** gap down after it (the third candle need not
gap away from the doji). Output is 0 or **-100** (purely bearish; no bullish or ±80
partial-penetration score). The ``penetration`` factor defaults to TA-Lib's 0.3 (how far below
the 1st close the black candle must close, as a fraction of the 1st real body).

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

# TA-Lib reports a lookback of max(BodyDoji, BodyLong, BodyShort) + 2 = 12 for CDLEVENINGDOJISTAR.
_LOOKBACK = 12

# TA-Lib's default penetration for CDLEVENINGDOJISTAR.
_DEFAULT_PENETRATION = 0.3


def evening_doji_star(df: pd.DataFrame, penetration: float = _DEFAULT_PENETRATION) -> pd.Series:
    """Evening Doji Star over ``df`` (OHLC) as a 0/-100 ``Series``.

    Matches ``talib.CDLEVENINGDOJISTAR`` bit-exactly: -100 where a long white candle is followed
    by a doji that gaps up, then a black candle that closes more than ``penetration`` of the first
    body below the first close, else 0. The first 12 bars are 0 (TA-Lib lookback).
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

        long_white_1 = (rb[first] > body_long[first]) & (color[first] == 1)  # NaN avg -> False
        doji_2 = rb[second] <= body_doji[second]
        gap_up_2 = body_lo[second] > body_hi[first]  # strict real-body gap up over the 1st body
        black_3 = (rb[third] > body_short[third]) & (color[third] == -1)
        deep_3 = c[third] < c[first] - rb[first] * penetration

        hit = long_white_1 & doji_2 & gap_up_2 & black_3 & deep_3
        out[2:] = np.where(hit, -100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 12 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class EveningDojiStar(Indicator):
    """Evening Doji Star candlestick pattern.

    What: a long white candle, then a gapped-up doji star, then a black candle that closes deep
    into the first body — a bearish top-reversal.
    Best settings: ``penetration`` (default 0.3) sets how far below the first close the black
    candle must close, as a fraction of the first real body.
    Edge cases: the gap up before the star is strict (no gap down required after it); output is
    only 0 or -100 (no bullish/partial score); first 12 bars are 0.
    Parity: TA-Lib ``CDLEVENINGDOJISTAR`` (BodyLong/BodyShort = RealBody/10/1.0,
    BodyDoji = HighLow/10/0.1, penetration 0.3), exact.
    """

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="evening_doji_star",
        category="candles",
        aliases=("EveningDojiStar", "CDLEVENINGDOJISTAR"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("evening_doji_star",),
        bounds={"evening_doji_star": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLEVENINGDOJISTAR",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        penetration: float = Field(
            default=_DEFAULT_PENETRATION,
            ge=0.0,
            description="Fraction of the first real body the black candle must close below "
            "the first close (TA-Lib default 0.3).",
        )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return evening_doji_star(df, penetration=self.params["penetration"])
