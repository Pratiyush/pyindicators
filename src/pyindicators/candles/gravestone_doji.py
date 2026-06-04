"""CDLGRAVESTONEDOJI — Gravestone Doji (single bar, non-directional).

A gravestone doji is a doji (negligible real body) that sits at the *bottom* of the bar:
a long upper shadow and (almost) no lower shadow, so open ≈ close ≈ low. TA-Lib::

    RealBody    <= BodyDoji average            # the body is a doji
    AND UpperShadow > ShadowVeryShort average  # a real (long) upper shadow
    AND LowerShadow < ShadowVeryShort average  # no meaningful lower shadow

where ``BodyDoji`` is ``(HighLow, 10, 0.1)`` and ``ShadowVeryShort`` is ``(HighLow, 10, 0.1)``.
The pattern is non-directional, so the output is 0 or +100 (never negative and never the ±80
partial-penetration score — there is no body-edge tie to penalise for this pattern).

Both driving settings have an averaging period of 10, so TA-Lib's lookback is 10 and the first
10 bars are forced to 0.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, lower_shadow, real_body, upper_shadow

# TA-Lib reports a lookback of max(BodyDoji, ShadowVeryShort) avg period = 10.
_LOOKBACK = 10


def gravestone_doji(df: pd.DataFrame) -> pd.Series:
    """Gravestone Doji pattern over ``df`` (OHLC) as a -100/0/100 ``Series`` (here 0 or 100).

    Matches ``talib.CDLGRAVESTONEDOJI`` bit-exactly: +100 where the body is a doji with a long
    upper shadow and a negligible lower shadow, 0 elsewhere. The first 10 bars are 0 (TA-Lib
    lookback); output is pure ±100 with no ±80 partial-penetration score.
    """
    rb = real_body(df).to_numpy()
    up = upper_shadow(df).to_numpy()
    low = lower_shadow(df).to_numpy()
    body_doji = candle_average(df, "BodyDoji").to_numpy()
    shadow_short = candle_average(df, "ShadowVeryShort").to_numpy()

    # NaN averages during warm-up make the comparisons False -> 0, matching TA-Lib's lookback.
    is_doji = rb <= body_doji
    long_upper = up > shadow_short
    short_lower = low < shadow_short
    hit = is_doji & long_upper & short_lower

    out = np.where(hit, 100.0, 0.0)
    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 10 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class GravestoneDoji(Indicator):
    """Gravestone Doji candlestick pattern.

    What: a doji with a long upper shadow and no lower shadow (open ≈ close ≈ low) — a bearish
    reversal hint where buyers drove price up but sellers pushed it back to the low.
    Best settings: parameterless; body ≤ 10% of the average range, upper shadow long, lower none.
    Edge cases: first 10 bars are 0 (TA-Lib lookback); output is pure 0/+100 (no ±80, no sign).
    Parity: TA-Lib ``CDLGRAVESTONEDOJI`` (BodyDoji = HighLow/10/0.1, ShadowVeryShort same), exact.
    """

    class Params(BaseModel):
        """Parameters for Gravestone Doji (TA-Lib ``CDLGRAVESTONEDOJI`` takes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="gravestone_doji",
        category="candles",
        aliases=("GravestoneDoji", "CDLGRAVESTONEDOJI"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("gravestone_doji",),
        bounds={"gravestone_doji": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLGRAVESTONEDOJI",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return gravestone_doji(df)
