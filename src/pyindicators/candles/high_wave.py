"""CDLHIGHWAVE — High-Wave Candle (single bar, directional sign, magnitude 100).

A high-wave candle has a *very short real body* with *extremely long* upper **and** lower
shadows — a wide-range bar of deep market indecision. TA-Lib's test::

    RealBody    < BodyShort average          # short body
    AND UpperShadow > ShadowVeryLong average  # very long upper shadow
    AND LowerShadow > ShadowVeryLong average  # very long lower shadow

``BodyShort`` is ``(RealBody, 10, 1.0)`` and ``ShadowVeryLong`` is ``(RealBody, 0, 2.0)`` — so
each shadow must exceed twice the bar's own real body (no shadow averaging window). Output is
+100 for a white candle / -100 for a black candle, else 0. There is no partial (±80) score.

The only setting with a non-zero averaging period is ``BodyShort`` (period 10), so TA-Lib's
lookback is 10 — the first 10 bars are forced to 0. ``CDLHIGHWAVE`` takes no parameters.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, lower_shadow, real_body, upper_shadow

# TA-Lib reports a lookback of 10 for CDLHIGHWAVE (BodyShort period 10; ShadowVeryLong is 0).
_LOOKBACK = 10


def high_wave(df: pd.DataFrame) -> pd.Series:
    """High-Wave Candle over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDLHIGHWAVE`` bit-exactly: a short real body with both shadows longer than
    twice that body; sign is the candle colour. The first 10 bars are 0 (TA-Lib lookback).
    """
    rb = real_body(df)
    body_short = candle_average(df, "BodyShort")  # RealBody/10/1.0
    shadow_very_long = candle_average(df, "ShadowVeryLong")  # RealBody/0/2.0
    hit = (
        (rb < body_short)  # NaN threshold during warm-up -> False -> 0
        & (upper_shadow(df) > shadow_very_long)
        & (lower_shadow(df) > shadow_very_long)
    )
    out = np.where(hit, candle_color(df).to_numpy() * 100.0, 0.0)
    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 10 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class HighWave(Indicator):
    """High-Wave candlestick.

    What: a single bar with a tiny body and very long upper and lower shadows — extreme
    indecision / volatility with no directional resolution.
    Best settings: parameterless; body < 10-bar average body, each shadow > 2x the body.
    Edge cases: first 10 bars are 0 (TA-Lib lookback); +100 white / -100 black.
    Parity: TA-Lib ``CDLHIGHWAVE`` (BodyShort = RealBody/10/1.0, ShadowVeryLong =
    RealBody/0/2.0), exact integer match.
    """

    spec = IndicatorSpec(
        name="high_wave",
        category="candles",
        aliases=("High Wave", "CDLHIGHWAVE"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("high_wave",),
        bounds={"high_wave": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLHIGHWAVE",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return high_wave(df)
