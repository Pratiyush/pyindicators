"""CDLSHOOTINGSTAR — Shooting Star pattern (single bar, bearish-only).

A shooting star is a small real body at the *bottom* of the bar's range, with a long upper
shadow and almost no lower shadow, that *gaps up* from the prior candle's body — a bearish
reversal hint after an advance. TA-Lib's test (all four must hold)::

    RealBody      < BodyShort  average        # small body
    UpperShadow   > ShadowLong average        # long upper wick
    LowerShadow   < ShadowVeryShort average   # negligible lower wick
    min(open, close)[cur] > max(open, close)[prev]   # body gaps up over previous body

Output is single-valued: **-100** on a hit, 0 otherwise (there is no bullish variant and no
±80 partial score — the pattern is a conjunction of strict inequalities, not an edge-tie test).

Driving CandleSettings: ``BodyShort = (RealBody, 10, 1.0)``, ``ShadowLong = (RealBody, 0, 1.0)``
(``ShadowLong`` has ``avgPeriod = 0`` so it compares against the *current* bar's real body),
``ShadowVeryShort = (HighLow, 10, 0.1)``. The 10-bar averages need 10 prior bars and the gap
test needs one prior bar, so TA-Lib's lookback is ``max(10, 0, 10) + 1 = 11``; the first 11
bars are forced to 0 to align bar-for-bar with ``talib.CDLSHOOTINGSTAR``.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, lower_shadow, real_body, upper_shadow

# TA-Lib lookback: max(BodyShort, ShadowLong, ShadowVeryShort avgPeriods) + 1 = max(10,0,10)+1.
_LOOKBACK = 11


def shooting_star(df: pd.DataFrame) -> pd.Series:
    """Shooting Star pattern over ``df`` (OHLC) as a -100/0 ``Series``.

    Matches ``talib.CDLSHOOTINGSTAR`` bit-exactly: -100 where the bar has a small body, a long
    upper shadow, a negligible lower shadow, and its body gaps up over the previous body; 0
    otherwise. The first 11 bars are 0 (TA-Lib lookback).
    """
    rb = real_body(df).to_numpy()
    upper = upper_shadow(df).to_numpy()
    lower = lower_shadow(df).to_numpy()
    body_short = candle_average(df, "BodyShort").to_numpy()
    shadow_long = candle_average(df, "ShadowLong").to_numpy()
    shadow_vs = candle_average(df, "ShadowVeryShort").to_numpy()

    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    body_hi = np.maximum(o, c)
    body_lo = np.minimum(o, c)

    n = len(c)
    out = np.zeros(n, dtype="float64")

    small_body = rb < body_short
    long_upper = upper > shadow_long
    short_lower = lower < shadow_vs
    gap_up = np.zeros(n, dtype=bool)
    gap_up[1:] = body_lo[1:] > body_hi[:-1]  # current body gaps up over previous body

    hit = small_body & long_upper & short_lower & gap_up  # NaN average -> False during warm-up
    out[hit] = -100.0

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 11 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class ShootingStar(Indicator):
    """Shooting Star candlestick pattern.

    What: a small body with a long upper shadow and tiny lower shadow that gaps up over the
    prior body — a bearish reversal signal after an advance.
    Best settings: parameterless; small body (BodyShort), long upper wick (ShadowLong vs the
    current body), negligible lower wick (ShadowVeryShort), body gapping up.
    Edge cases: bearish-only (output is -100 or 0, never positive); first 11 bars are 0.
    Parity: TA-Lib ``CDLSHOOTINGSTAR`` (BodyShort/ShadowLong/ShadowVeryShort), exact integer.
    """

    class Params(BaseModel):
        """Parameters for Shooting Star (TA-Lib ``CDLSHOOTINGSTAR`` takes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="shooting_star",
        category="candles",
        aliases=("ShootingStar", "CDLSHOOTINGSTAR"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("shooting_star",),
        bounds={"shooting_star": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLSHOOTINGSTAR",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return shooting_star(df)
