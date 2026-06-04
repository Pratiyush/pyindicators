"""CDLMATHOLD — Mat Hold (five bars, bullish continuation).

A long white candle, then three small "reaction" candles that gap up but drift back down
(holding within the first body, penetrating it by less than ``penetration``), then a long
white candle that closes above the whole reaction. A bullish continuation pattern. TA-Lib::

    RealBody(i-4) > BodyLong average(i-4)                 # 1st: long body
    AND RealBody(i-3) < BodyShort average(i-3)            # 2nd: small body
    AND RealBody(i-2) < BodyShort average(i-2)            # 3rd: small body
    AND RealBody(i-1) < BodyShort average(i-1)            # 4th: small body
    AND color(i-4) == white AND color(i-3) == black AND color(i) == white
    AND RealBodyGapUp(i-3, i-4)                           # 2nd body gaps above the 1st body
    AND min(open,close)[i-2] <  close(i-4)               # 3rd/4th hold within the 1st body ...
    AND min(open,close)[i-1] <  close(i-4)
    AND min(open,close)[i-2] >  close(i-4) - RealBody(i-4) * penetration   # ... shallowly
    AND min(open,close)[i-1] >  close(i-4) - RealBody(i-4) * penetration
    AND max(open,close)[i-2] <  open(i-3)                 # 2nd -> 4th are falling
    AND max(open,close)[i-1] <  max(open,close)[i-2]
    AND open(i)  > close(i-1)                             # 5th opens above the prior close
    AND close(i) > max(high[i-3], high[i-2], high[i-1])   # 5th closes above the reaction highs

Output is 0 or **+100** (purely bullish; there is no bearish or partial-penetration ±80
score for this pattern). The ``penetration`` factor defaults to TA-Lib's 0.5 (how deep the
reaction candles may dip into the first real body, as a fraction of that body).

``RealBodyGapUp(IDX2, IDX1)`` is ``min(open,close)[IDX2] > max(open,close)[IDX1]`` — the 2nd
body sits entirely above the 1st body. Both ``BodyLong`` and ``BodyShort`` are
``(RealBody, 10, 1.0)``; the longest average period is 10 and the pattern spans four prior
bars, so TA-Lib's lookback is ``max(10, 10) + 4 = 14`` (the first 14 bars are forced to 0).
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body

# TA-Lib lookback for CDLMATHOLD: max(BodyShort, BodyLong) avgPeriod (10) + 4 prior bars.
_LOOKBACK = 14

# TA-Lib's default penetration for CDLMATHOLD.
_DEFAULT_PENETRATION = 0.5


def mat_hold(df: pd.DataFrame, penetration: float = _DEFAULT_PENETRATION) -> pd.Series:
    """Mat Hold over ``df`` (OHLC) as a 0/100 ``Series``.

    Matches ``talib.CDLMATHOLD`` bit-exactly: +100 where a long white candle is followed by
    three small reaction candles that gap up and hold shallowly within the first body, then a
    long white candle closing above the reaction's highs; else 0. The first 14 bars are 0
    (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    h = df[HIGH].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    body_short = candle_average(df, "BodyShort").to_numpy()
    color = candle_color(df).to_numpy()
    body_hi = np.maximum(o, c)
    body_lo = np.minimum(o, c)
    n = len(c)
    out = np.zeros(n, dtype="float64")

    if n > 4:
        # Slice alignment: index j of each slice is the current bar i = j + 4.
        #   c1 = i-4 -> [:-4]   c2 = i-3 -> [1:-3]   c3 = i-2 -> [2:-2]
        #   c4 = i-1 -> [3:-1]  c5 = i   -> [4:]
        c1_rb = rb[:-4]
        c1_long = c1_rb > body_long[:-4]  # NaN average -> False
        c1_white = color[:-4] == 1
        c1_close = c[:-4]
        c1_floor = c1_close - c1_rb * penetration  # shallowest allowed reaction low

        c2_short = rb[1:-3] < body_short[1:-3]
        c2_black = color[1:-3] == -1
        c2_open = o[1:-3]
        c2_body_lo = body_lo[1:-3]
        c2_high = h[1:-3]
        c2_gap_up = c2_body_lo > body_hi[:-4]  # RealBodyGapUp(i-3, i-4)

        c3_short = rb[2:-2] < body_short[2:-2]
        c3_body_hi = body_hi[2:-2]
        c3_body_lo = body_lo[2:-2]
        c3_high = h[2:-2]

        c4_short = rb[3:-1] < body_short[3:-1]
        c4_body_hi = body_hi[3:-1]
        c4_body_lo = body_lo[3:-1]
        c4_high = h[3:-1]
        c4_close = c[3:-1]

        c5_white = color[4:] == 1
        c5_open = o[4:]
        c5_close = c[4:]

        reaction_high = np.maximum(np.maximum(c2_high, c3_high), c4_high)

        hit = (
            c1_long
            & c2_short
            & c3_short
            & c4_short
            & c1_white
            & c2_black
            & c5_white
            & c2_gap_up
            # 3rd/4th bodies dip into, but hold within (and shallowly into) the 1st body
            & (c3_body_lo < c1_close)
            & (c4_body_lo < c1_close)
            & (c3_body_lo > c1_floor)
            & (c4_body_lo > c1_floor)
            # 2nd -> 4th are falling
            & (c3_body_hi < c2_open)
            & (c4_body_hi < c3_body_hi)
            # 5th opens above the prior close and closes above the reaction's highs
            & (c5_open > c4_close)
            & (c5_close > reaction_high)
        )
        out[4:] = np.where(hit, 100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 14 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class MatHold(Indicator):
    """Mat Hold candlestick pattern.

    What: a long white candle, three small reaction candles that gap up then drift back while
    holding within the first body, and a long white candle closing above the reaction — a
    bullish continuation signal.
    Best settings: ``penetration`` (default 0.5) caps how deep the reaction candles may dip
    into the first real body, as a fraction of that body.
    Edge cases: output is only 0 or +100 (no bearish/partial score); first 14 bars are 0.
    Parity: TA-Lib ``CDLMATHOLD`` (BodyLong/BodyShort = RealBody/10/1.0, penetration 0.5),
    exact integer match.
    """

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="mat_hold",
        category="candles",
        aliases=("MatHold", "CDLMATHOLD"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("mat_hold",),
        bounds={"mat_hold": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLMATHOLD",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        penetration: float = Field(
            default=_DEFAULT_PENETRATION,
            ge=0.0,
            description="Fraction of the first real body the reaction candles may dip into "
            "(TA-Lib default 0.5).",
        )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return mat_hold(df, penetration=self.params["penetration"])
