"""CDLSHORTLINE — Short Line Candle (single bar, directional sign, magnitude 100).

A short line candle has a *short real body* with *short* upper **and** lower shadows — a
small, quiet bar with little wicking (the small-bodied counterpart of CDLLONGLINE). TA-Lib's
test::

    RealBody    < BodyShort average            # short body
    AND UpperShadow < ShadowShort average       # short upper shadow
    AND LowerShadow < ShadowShort average       # short lower shadow

``BodyShort`` is ``(RealBody, 10, 1.0)`` and ``ShadowShort`` is ``(Shadows, 10, 1.0)``. Output
is +100 for a white candle / -100 for a black candle, else 0. There is no partial (±80) score.

Both driving settings use a 10-bar averaging window, so TA-Lib's lookback is 10 — the first 10
bars are forced to 0. ``CDLSHORTLINE`` takes no parameters.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, lower_shadow, real_body, upper_shadow

# TA-Lib reports a lookback of 10 for CDLSHORTLINE (BodyShort and ShadowShort period 10).
_LOOKBACK = 10


def short_line(df: pd.DataFrame) -> pd.Series:
    """Short Line Candle over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDLSHORTLINE`` bit-exactly: a short real body with both shadows shorter than
    the ShadowShort average; sign is the candle colour. The first 10 bars are 0 (TA-Lib
    lookback).
    """
    rb = real_body(df)
    body_short = candle_average(df, "BodyShort")  # RealBody/10/1.0
    shadow_short = candle_average(df, "ShadowShort")  # Shadows/10/1.0
    hit = (
        (rb < body_short)  # NaN threshold during warm-up -> False -> 0
        & (upper_shadow(df) < shadow_short)
        & (lower_shadow(df) < shadow_short)
    )
    out = np.where(hit, candle_color(df).to_numpy() * 100.0, 0.0)
    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 10 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class ShortLine(Indicator):
    """Short Line candlestick.

    What: a single bar with a short real body and short upper and lower shadows — a small,
    quiet bar (the small-bodied counterpart of the Long Line candle).
    Best settings: parameterless; body < 10-bar average body, each shadow < the ShadowShort
    average over the prior 10 bars.
    Edge cases: first 10 bars are 0 (TA-Lib lookback); +100 white / -100 black.
    Parity: TA-Lib ``CDLSHORTLINE`` (BodyShort = RealBody/10/1.0, ShadowShort = Shadows/10/1.0),
    exact integer match.
    """

    spec = IndicatorSpec(
        name="short_line",
        category="candles",
        aliases=("Short Line", "CDLSHORTLINE"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("short_line",),
        bounds={"short_line": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLSHORTLINE",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return short_line(df)
