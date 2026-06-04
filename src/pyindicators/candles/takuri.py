"""CDLTAKURI — Takuri line (single bar, non-directional).

A Takuri is a Dragonfly Doji with an *exceptionally* long lower shadow: a doji (negligible
real body) whose price probed far down and recovered to close at the top of the bar, leaving
essentially no upper shadow. It differs from the dragonfly doji only in the lower-shadow test
— the lower wick must clear the much taller ``ShadowVeryLong`` threshold. TA-Lib's test (all
three must hold)::

    RealBody     <= BodyDoji         average   # tiny body  (HighLow / 10 / 0.1)
    UpperShadow  <  ShadowVeryShort  average   # no upper wick   (HighLow / 10 / 0.1)
    LowerShadow  >  ShadowVeryLong   average   # *very* long lower wick (RealBody / 0 / 2.0)

Output is 0 or 100 (no bullish/bearish direction; the Takuri itself is the signal). The two
period-10 settings (``BodyDoji`` and ``ShadowVeryShort``) drive the lookback; ``ShadowVeryLong``
has ``AvgPeriod == 0`` (it uses the current bar's own real body), so TA-Lib's lookback is 10
and the first 10 bars are forced to 0.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, lower_shadow, real_body, upper_shadow

# TA-Lib reports a lookback of 10 for CDLTAKURI (BodyDoji / ShadowVeryShort period 10;
# ShadowVeryLong has AvgPeriod 0 and so adds no warm-up of its own).
_LOOKBACK = 10


def takuri(df: pd.DataFrame) -> pd.Series:
    """Takuri pattern over ``df`` (OHLC) as a -100/0/100 ``Series`` (here 0 or 100).

    Matches ``talib.CDLTAKURI`` bit-exactly: 100 where the bar is a doji with a *very* long
    lower shadow and no upper shadow, 0 elsewhere, and 0 during the 10-bar warm-up where the
    period-10 averages are undefined.
    """
    rb = real_body(df).to_numpy()
    body_doji = candle_average(df, "BodyDoji").to_numpy()
    shadow_vs = candle_average(df, "ShadowVeryShort").to_numpy()
    shadow_vl = candle_average(df, "ShadowVeryLong").to_numpy()
    upper = upper_shadow(df).to_numpy()
    lower = lower_shadow(df).to_numpy()

    # NaN averages during warm-up -> comparisons are False -> 0, matching TA-Lib's lookback.
    hit = (rb <= body_doji) & (upper < shadow_vs) & (lower > shadow_vl)
    out = np.where(hit, 100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 10 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class Takuri(Indicator):
    """Takuri candlestick pattern (dragonfly doji with a very long lower shadow).

    What: a doji with essentially no upper shadow and an unusually long lower shadow — price
    was driven sharply lower and recovered to close at the open/high; a strong potential
    bullish reversal at the bottom of a downtrend.
    Best settings: parameterless; body is a doji (<=10% of the 10-bar range), the upper shadow
    falls below the ShadowVeryShort threshold, and the lower shadow exceeds the ShadowVeryLong
    threshold (twice the bar's own real body).
    Edge cases: non-directional (0 or 100); first 10 bars are 0 (TA-Lib lookback).
    Parity: TA-Lib ``CDLTAKURI`` (BodyDoji/ShadowVeryShort = HighLow/10/0.1, ShadowVeryLong =
    RealBody/0/2.0), exact integer match.
    """

    class Params(BaseModel):
        """Parameters for Takuri (TA-Lib ``CDLTAKURI`` takes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="takuri",
        category="candles",
        aliases=("Takuri", "CDLTAKURI"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("takuri",),
        bounds={"takuri": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLTAKURI",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return takuri(df)
