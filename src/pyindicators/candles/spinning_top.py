"""CDLSPINNINGTOP — Spinning Top candlestick (single bar, directional sign, magnitude 100).

A spinning top has a small body with upper and lower shadows that both exceed the body —
indecision with a wide trading range. TA-Lib's test::

    RealBody < BodyShort average
    AND upper_shadow > RealBody
    AND lower_shadow > RealBody

``BodyShort`` is ``(RealBody, 10, 1.0)``. The shadow comparisons are against the bar's own
real body (no averaging). Output is +100 white / -100 black, else 0.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, lower_shadow, real_body, upper_shadow


def spinning_top(df: pd.DataFrame) -> pd.Series:
    """Spinning Top pattern over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDLSPINNINGTOP`` bit-exactly: short body with both shadows longer than the
    body; sign is the candle colour. The first 10 bars are 0 (TA-Lib lookback).
    """
    rb = real_body(df)
    body_short = candle_average(df, "BodyShort")
    hit = (rb < body_short) & (upper_shadow(df) > rb) & (lower_shadow(df) > rb)
    return pd.Series(np.where(hit, candle_color(df).to_numpy() * 100.0, 0.0), index=df.index)


@INDICATORS.register
class SpinningTop(Indicator):
    """Spinning Top candlestick.

    What: a small body flanked by longer upper and lower shadows — indecision.
    Best settings: parameterless; body < 10-bar average body, both shadows > the body.
    Edge cases: first 10 bars are 0; +100 white / -100 black.
    Parity: TA-Lib ``CDLSPINNINGTOP`` (BodyShort = RealBody/10/1.0), exact integer match.
    """

    spec = IndicatorSpec(
        name="spinning_top",
        category="candles",
        aliases=("Spinning Top", "CDLSPINNINGTOP"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("spinning_top",),
        bounds={"spinning_top": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLSPINNINGTOP",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return spinning_top(df)
