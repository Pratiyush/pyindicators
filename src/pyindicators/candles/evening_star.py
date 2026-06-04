"""CDLEVENINGSTAR — Evening Star pattern (three bars, bearish reversal).

A bearish top reversal: a long white candle, then a small-bodied "star" that gaps its body
*above* the first, then a black candle that closes well down into the first white body. TA-Lib's
``CDLEVENINGSTAR``::

    1st candle: white AND RealBody(1st) > BodyLong average(1st)        # long white body
    2nd candle: RealBody(2nd) <= BodyShort average(2nd)               # short "star" body
                AND min(o,c)[2nd] > max(o,c)[1st]                     # real body gaps up over 1st
    3rd candle: black                                                 # black body
                AND RealBody(3rd) > BodyShort average(3rd)            # not itself a short body
                AND close(3rd) < close(1st) - RealBody(1st) * penetration   # deep into 1st body

The star's body need only gap above the first body (``min(o,c)`` of the star strictly above
``max(o,c)`` of the first); the third candle merely has to be black and not short, and close
more than ``penetration`` of the first real body below the first close. Every qualifying edge is
a strict inequality, so a body that only *touches* a boundary does not qualify — there is no
partial-penetration score here; the output is only -100 or 0 (TA-Lib emits no bullish variant
and no ±80 for this pattern).

The ``penetration`` factor defaults to TA-Lib's 0.3 (how far below the first close the black
candle must close, as a fraction of the first real body). ``BodyLong`` and ``BodyShort`` are both
``(RealBody, 10, 1.0)``; the first candle's long-body average needs 10 prior bars and the first
candle is two bars back, so TA-Lib's lookback is ``10 + 2 = 12`` (the first 12 bars are 0).
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body

# TA-Lib reports a lookback of 12 for CDLEVENINGSTAR (BodyLong period 10 on the first of 3 bars).
_LOOKBACK = 12

# TA-Lib's default penetration for CDLEVENINGSTAR.
_DEFAULT_PENETRATION = 0.3


def evening_star(df: pd.DataFrame, penetration: float = _DEFAULT_PENETRATION) -> pd.Series:
    """Evening Star pattern over ``df`` (OHLC) as a -100/0 ``Series``.

    Matches ``talib.CDLEVENINGSTAR`` bit-exactly: -100 at the third bar of an Evening Star
    formation (long white, gapped-up short star, black candle closing more than ``penetration``
    of the first real body below the first close), 0 elsewhere. All comparisons are strict, so
    there is no ±80 partial score. The first 12 bars are 0 (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    body_short = candle_average(df, "BodyShort").to_numpy()
    color = candle_color(df).to_numpy()
    body_hi = np.maximum(o, c)
    body_lo = np.minimum(o, c)
    n = len(c)
    out = np.zeros(n, dtype="float64")

    # Triplet (1st, 2nd, 3rd) = bars (i-2, i-1, i) for i in [2 .. n-1].
    first_white_long = (color[:-2] == 1) & (rb[:-2] > body_long[:-2])  # NaN average -> False
    star_short_gap = (rb[1:-1] <= body_short[1:-1]) & (body_lo[1:-1] > body_hi[:-2])
    third_black_long = (color[2:] == -1) & (rb[2:] > body_short[2:])
    deep = c[2:] < c[:-2] - rb[:-2] * penetration

    hit = first_white_long & star_short_gap & third_black_long & deep
    out[2:] = np.where(hit, -100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 12 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class EveningStar(Indicator):
    """Evening Star candlestick pattern.

    What: a long white candle, then a small-bodied star gapping above it, then a black candle
        closing deep into the first body — a bearish reversal at a top.
    Best settings: ``penetration`` (default 0.3) sets how far below the first close the black
        candle must close, as a fraction of the first real body.
    Edge cases: every qualifying edge is strict, so a touching boundary gives 0 (no ±80); the
        output is bearish only (-100) or absent (0); first 12 bars are 0 (TA-Lib lookback).
    Parity: TA-Lib ``CDLEVENINGSTAR`` (BodyLong/BodyShort = RealBody/10/1.0, penetration 0.3),
        exact integer match.
    """

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="evening_star",
        category="candles",
        aliases=("EveningStar", "CDLEVENINGSTAR"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("evening_star",),
        bounds={"evening_star": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLEVENINGSTAR",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        penetration: float = Field(
            default=_DEFAULT_PENETRATION,
            ge=0.0,
            description="Fraction of the first real body the black candle must close below the "
            "first close (TA-Lib default 0.3).",
        )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return evening_star(df, penetration=self.params["penetration"])
