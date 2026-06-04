"""CDLLONGLEGGEDDOJI — Long-Legged Doji (single bar, non-directional).

A long-legged doji is a doji (negligible real body) with at least one *long* shadow — open
and close cluster together while price ranged far in one or both directions, a wide-range bar
of deep indecision. TA-Lib's test::

    RealBody    <= BodyDoji average                                  # the body is a doji
    AND ( UpperShadow > ShadowLong average                           # a long upper shadow ...
          OR LowerShadow > ShadowLong average )                      # ... or a long lower one

where ``BodyDoji`` is ``(HighLow, 10, 0.1)`` and ``ShadowLong`` is ``(RealBody, 0, 1.0)`` — a
shadow is "long" when it exceeds the bar's own real body (no shadow averaging window). The
pattern is non-directional, so the output is 0 or +100 (never negative and never the ±80
partial-penetration score — there is no body-edge tie to penalise for this pattern).

The only setting with a non-zero averaging period is ``BodyDoji`` (period 10), so TA-Lib's
lookback is 10 and the first 10 bars are forced to 0. ``CDLLONGLEGGEDDOJI`` takes no parameters.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, lower_shadow, real_body, upper_shadow

# TA-Lib reports a lookback of 10 for CDLLONGLEGGEDDOJI (BodyDoji period 10; ShadowLong is 0).
_LOOKBACK = 10


def long_legged_doji(df: pd.DataFrame) -> pd.Series:
    """Long-Legged Doji pattern over ``df`` (OHLC) as a -100/0/100 ``Series`` (here 0 or 100).

    Matches ``talib.CDLLONGLEGGEDDOJI`` bit-exactly: +100 where the body is a doji and at least
    one shadow is longer than the real body, 0 elsewhere. The first 10 bars are 0 (TA-Lib
    lookback); output is pure 0/+100 with no sign and no ±80 partial-penetration score.
    """
    rb = real_body(df).to_numpy()
    body_doji = candle_average(df, "BodyDoji").to_numpy()  # HighLow/10/0.1
    shadow_long = candle_average(df, "ShadowLong").to_numpy()  # RealBody/0/1.0
    up = upper_shadow(df).to_numpy()
    low = lower_shadow(df).to_numpy()

    # NaN averages during warm-up make the comparisons False -> 0, matching TA-Lib's lookback.
    is_doji = rb <= body_doji
    long_shadow = (up > shadow_long) | (low > shadow_long)
    hit = is_doji & long_shadow

    out = np.where(hit, 100.0, 0.0)
    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 10 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class LongLeggedDoji(Indicator):
    """Long-Legged Doji candlestick pattern.

    What: a doji (open ≈ close) with one or both shadows long — price ranged widely but closed
    near the open, signalling pronounced market indecision.
    Best settings: parameterless; body ≤ 10% of the average 10-bar range, and at least one shadow
    longer than the bar's own real body.
    Edge cases: non-directional (0 or +100); first 10 bars are 0 (TA-Lib lookback); no ±80 score.
    Parity: TA-Lib ``CDLLONGLEGGEDDOJI`` (BodyDoji = HighLow/10/0.1, ShadowLong = RealBody/0/1.0),
    exact integer match.
    """

    class Params(BaseModel):
        """Parameters for Long-Legged Doji (TA-Lib ``CDLLONGLEGGEDDOJI`` takes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="long_legged_doji",
        category="candles",
        aliases=("LongLeggedDoji", "CDLLONGLEGGEDDOJI"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("long_legged_doji",),
        bounds={"long_legged_doji": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLLONGLEGGEDDOJI",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return long_legged_doji(df)
