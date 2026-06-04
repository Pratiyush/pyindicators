"""CDLMARUBOZU — Marubozu candlestick (single bar, directional sign, magnitude 100).

A marubozu is a long-bodied candle with no (or negligible) shadows: the body spans the whole
range. TA-Lib's test::

    RealBody > BodyLong average            # long body
    AND upper_shadow < ShadowVeryShort average
    AND lower_shadow < ShadowVeryShort average

``BodyLong`` is ``(RealBody, 10, 1.0)`` and ``ShadowVeryShort`` is ``(HighLow, 10, 0.1)``.
Output is +100 for a white marubozu, -100 for a black one, else 0.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, lower_shadow, real_body, upper_shadow


def marubozu(df: pd.DataFrame) -> pd.Series:
    """Marubozu pattern over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDLMARUBOZU`` bit-exactly: long body with very short shadows; sign is the
    candle colour (+1 white / -1 black). The first 10 bars are 0 (TA-Lib lookback).
    """
    rb = real_body(df)
    body_long = candle_average(df, "BodyLong")
    very_short = candle_average(df, "ShadowVeryShort")
    hit = (rb > body_long) & (upper_shadow(df) < very_short) & (lower_shadow(df) < very_short)
    return pd.Series(np.where(hit, candle_color(df).to_numpy() * 100.0, 0.0), index=df.index)


@INDICATORS.register
class Marubozu(Indicator):
    """Marubozu candlestick.

    What: a long body with no meaningful shadows — strong one-directional conviction.
    Best settings: parameterless; body > 10-bar average body, shadows < 10% of average range.
    Edge cases: first 10 bars are 0; +100 white / -100 black.
    Parity: TA-Lib ``CDLMARUBOZU`` (BodyLong = RealBody/10/1.0, ShadowVeryShort =
    HighLow/10/0.1), exact integer match.
    """

    spec = IndicatorSpec(
        name="marubozu",
        category="candles",
        aliases=("Marubozu", "CDLMARUBOZU"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("marubozu",),
        bounds={"marubozu": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLMARUBOZU",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return marubozu(df)
