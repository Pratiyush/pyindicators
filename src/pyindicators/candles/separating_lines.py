"""CDLSEPARATINGLINES — Separating Lines pattern (two bars, bidirectional).

Two opposite-colour candles that share the *same open*, the second being a belt-hold that
continues the prior trend. TA-Lib::

    CandleColor(prev) == -CandleColor(cur)                 # opposite colours
    AND |open[cur] - open[prev]| <= Equal average(prev)    # same open (within Equal threshold)
    AND RealBody(cur) > BodyLong average(cur)              # current is a long body ...
    AND ( cur white: lower_shadow(cur) < ShadowVeryShort   # ... bullish belt-hold (no lower wick)
          cur black: upper_shadow(cur) < ShadowVeryShort ) #     bearish belt-hold (no upper wick)

Output is the current candle's colour times 100: +100 bullish (white after black), -100
bearish (black after white), 0 otherwise. There is no partial ±80 score for this pattern —
the "same open" tie is absorbed by the ``Equal`` threshold, so the result is pure ±100/0.

Settings: ``Equal`` = ``(HighLow, 5, 0.05)``, ``BodyLong`` = ``(RealBody, 10, 1.0)``,
``ShadowVeryShort`` = ``(HighLow, 10, 0.1)``. ``BodyLong``'s 10-bar average drives TA-Lib's
lookback of 11, so the first 11 bars are forced to 0.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import (
    candle_average,
    candle_color,
    lower_shadow,
    real_body,
    upper_shadow,
)

# TA-Lib reports a lookback of 11 for CDLSEPARATINGLINES (BodyLong period 10 + the prior bar).
_LOOKBACK = 11


def separating_lines(df: pd.DataFrame) -> pd.Series:
    """Separating Lines pattern over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDLSEPARATINGLINES`` bit-exactly: opposite-colour candles sharing the same
    open (within the ``Equal`` threshold) where the current candle is a long-bodied belt-hold.
    Sign is the current candle's colour. The first 11 bars are 0 (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    up = upper_shadow(df).to_numpy()
    lo = lower_shadow(df).to_numpy()
    color = candle_color(df).to_numpy()
    equal = candle_average(df, "Equal").to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    shadow_vs = candle_average(df, "ShadowVeryShort").to_numpy()
    n = len(o)
    out = np.zeros(n, dtype="float64")

    # Previous = bars [0..n-2], current = bars [1..n-1].
    cur_col = color[1:]
    prev_col = color[:-1]
    opposite = prev_col == -cur_col
    # Same open: current open within the previous bar's Equal threshold of the previous open.
    same_open = (o[1:] <= o[:-1] + equal[:-1]) & (o[1:] >= o[:-1] - equal[:-1])
    long_body = rb[1:] > body_long[1:]  # NaN average during warm-up -> False
    # Belt-hold: white candle has a negligible lower shadow; black candle a negligible upper.
    belt = np.where(cur_col == 1, lo[1:] < shadow_vs[1:], up[1:] < shadow_vs[1:])

    hit = opposite & same_open & long_body & belt
    out[1:] = np.where(hit, cur_col * 100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 11 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class SeparatingLines(Indicator):
    """Separating Lines candlestick pattern.

    What: two opposite-colour candles sharing the same open, the second a long belt-hold that
    resumes the prior trend — a continuation signal (+100 bullish, -100 bearish).
    Best settings: parameterless; "same open" is within the Equal threshold, the belt-hold is a
    long body with a very short trailing shadow.
    Edge cases: pure ±100/0 (no partial score); first 11 bars are 0 (TA-Lib lookback).
    Parity: TA-Lib ``CDLSEPARATINGLINES`` (Equal/BodyLong/ShadowVeryShort), exact integer match.
    """

    class Params(BaseModel):
        """Parameters for Separating Lines (TA-Lib ``CDLSEPARATINGLINES`` takes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="separating_lines",
        category="candles",
        aliases=("SeparatingLines", "CDLSEPARATINGLINES"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("separating_lines",),
        bounds={"separating_lines": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLSEPARATINGLINES",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return separating_lines(df)
