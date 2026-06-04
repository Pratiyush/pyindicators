"""CDLLONGLINE — Long Line Candle (single bar, directional sign, magnitude 100).

A long line candle has a *long real body* with *short* upper **and** lower shadows — a
decisive, wide-bodied bar with little wicking. TA-Lib's test::

    RealBody    > BodyLong average            # long body
    AND UpperShadow < ShadowShort average      # short upper shadow
    AND LowerShadow < ShadowShort average      # short lower shadow

``BodyLong`` is ``(RealBody, 10, 1.0)`` and ``ShadowShort`` is ``(Shadows, 10, 1.0)``. Output
is +100 for a white candle / -100 for a black candle, else 0. There is no partial (±80) score.

Both driving settings use a 10-bar averaging window, so TA-Lib's lookback is 10 — the first 10
bars are forced to 0. ``CDLLONGLINE`` takes no parameters.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, lower_shadow, real_body, upper_shadow

# TA-Lib reports a lookback of 10 for CDLLONGLINE (BodyLong and ShadowShort period 10).
_LOOKBACK = 10


def long_line(df: pd.DataFrame) -> pd.Series:
    """Long Line Candle over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDLLONGLINE`` bit-exactly: a long real body with both shadows shorter than
    the ShadowShort average; sign is the candle colour. The first 10 bars are 0 (TA-Lib
    lookback).
    """
    rb = real_body(df)
    body_long = candle_average(df, "BodyLong")  # RealBody/10/1.0
    shadow_short = candle_average(df, "ShadowShort")  # Shadows/10/1.0
    hit = (
        (rb > body_long)  # NaN threshold during warm-up -> False -> 0
        & (upper_shadow(df) < shadow_short)
        & (lower_shadow(df) < shadow_short)
    )
    out = np.where(hit, candle_color(df).to_numpy() * 100.0, 0.0)
    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 10 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class LongLine(Indicator):
    """Long Line candlestick.

    What: a single bar with a long real body and short upper and lower shadows — a decisive
    directional move with little intrabar reversal.
    Best settings: parameterless; body > 10-bar average body, each shadow < the ShadowShort
    average over the prior 10 bars.
    Edge cases: first 10 bars are 0 (TA-Lib lookback); +100 white / -100 black.
    Parity: TA-Lib ``CDLLONGLINE`` (BodyLong = RealBody/10/1.0, ShadowShort = Shadows/10/1.0),
    exact integer match.
    """

    spec = IndicatorSpec(
        name="long_line",
        category="candles",
        aliases=("Long Line", "CDLLONGLINE"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("long_line",),
        bounds={"long_line": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLLONGLINE",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return long_line(df)
