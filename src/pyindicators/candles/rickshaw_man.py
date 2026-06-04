"""CDLRICKSHAWMAN — Rickshaw Man (single bar, non-directional).

A rickshaw man is a long-legged doji whose tiny real body sits *near the middle* of an
otherwise wide bar: open and close cluster together, both shadows are long, and the body
straddles the high-low midpoint. It is the doji of deepest indecision — price ranged far in
*both* directions yet finished where it started, dead-centre. TA-Lib's test::

    RealBody    <= BodyDoji average                  # the body is a doji
    AND LowerShadow > ShadowLong average             # a long lower shadow
    AND UpperShadow > ShadowLong average             # a long upper shadow
    AND min(open, close) <= low + range/2 + Near average   # body near the midpoint ...
    AND max(open, close) >= low + range/2 - Near average   # ... within a Near tolerance band

where ``BodyDoji`` is ``(HighLow, 10, 0.1)``, ``ShadowLong`` is ``(RealBody, 0, 1.0)`` (a shadow
is "long" when it exceeds the bar's own real body, no shadow averaging window), and ``Near`` is
``(HighLow, 5, 0.2)`` — the body's two edges must each fall within a ``Near``-sized band around
the bar's high-low midpoint. The pattern is non-directional, so the output is 0 or +100 (never
negative and never the ±80 partial-penetration score — there is no body-edge tie to penalise).

The driving averaging periods are ``BodyDoji`` (10), ``ShadowLong`` (0) and ``Near`` (5), so
TA-Lib's lookback is ``max(10, 0, 5) = 10`` and the first 10 bars are forced to 0.
``CDLRICKSHAWMAN`` takes no parameters.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, hl_range, lower_shadow, real_body, upper_shadow

# TA-Lib lookback = max(BodyDoji=10, ShadowLong=0, Near=5) = 10.
_LOOKBACK = 10


def rickshaw_man(df: pd.DataFrame) -> pd.Series:
    """Rickshaw Man pattern over ``df`` (OHLC) as a -100/0/100 ``Series`` (here 0 or 100).

    Matches ``talib.CDLRICKSHAWMAN`` bit-exactly: +100 where the body is a doji with both
    shadows long and the body straddling the high-low midpoint within a ``Near`` band, 0
    elsewhere. The first 10 bars are 0 (TA-Lib lookback); output is pure 0/+100 with no sign
    and no ±80 partial-penetration score.
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    low = df[LOW].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    up = upper_shadow(df).to_numpy()
    lo_shadow = lower_shadow(df).to_numpy()
    rng = hl_range(df).to_numpy()
    body_doji = candle_average(df, "BodyDoji").to_numpy()  # HighLow/10/0.1
    shadow_long = candle_average(df, "ShadowLong").to_numpy()  # RealBody/0/1.0
    near = candle_average(df, "Near").to_numpy()  # HighLow/5/0.2

    body_hi = np.maximum(o, c)
    body_lo = np.minimum(o, c)
    midpoint = low + rng / 2.0

    # NaN averages during warm-up make the comparisons False -> 0, matching TA-Lib's lookback.
    is_doji = rb <= body_doji
    long_shadows = (lo_shadow > shadow_long) & (up > shadow_long)
    near_midpoint = (body_lo <= midpoint + near) & (body_hi >= midpoint - near)
    hit = is_doji & long_shadows & near_midpoint

    out = np.where(hit, 100.0, 0.0)
    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 10 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class RickshawMan(Indicator):
    """Rickshaw Man candlestick pattern.

    What: a long-legged doji with a tiny body sitting near the middle of a wide bar — both
    shadows long and open ≈ close ≈ the high-low midpoint, signalling extreme indecision.
    Best settings: parameterless; body ≤ 10% of the average 10-bar range, each shadow longer
    than the bar's own real body, and the body straddling the midpoint within a Near band.
    Edge cases: non-directional (0 or +100); first 10 bars are 0 (TA-Lib lookback); no ±80 score.
    Parity: TA-Lib ``CDLRICKSHAWMAN`` (BodyDoji = HighLow/10/0.1, ShadowLong = RealBody/0/1.0,
    Near = HighLow/5/0.2), exact integer match.
    """

    class Params(BaseModel):
        """Parameters for Rickshaw Man (TA-Lib ``CDLRICKSHAWMAN`` takes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="rickshaw_man",
        category="candles",
        aliases=("RickshawMan", "CDLRICKSHAWMAN"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("rickshaw_man",),
        bounds={"rickshaw_man": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLRICKSHAWMAN",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return rickshaw_man(df)
