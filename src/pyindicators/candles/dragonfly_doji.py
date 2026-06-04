"""CDLDRAGONFLYDOJI — Dragonfly Doji candlestick (single bar, non-directional).

A dragonfly doji is a doji (negligible real body) with a long lower shadow and essentially
no upper shadow — open, high and close cluster at the top of the bar while price probed far
down and recovered. TA-Lib's test (all three must hold)::

    RealBody     <= BodyDoji         average   # tiny body  (HighLow / 10 / 0.1)
    LowerShadow  >  ShadowVeryShort  average   # long lower wick
    UpperShadow  <  ShadowVeryShort  average   # no upper wick   (HighLow / 10 / 0.1)

Output is 0 or 100 (no bullish/bearish direction; the dragonfly itself is the signal). Both
driving settings (``BodyDoji`` and ``ShadowVeryShort``) use a 10-bar average, so TA-Lib's
lookback is 10 and the first 10 bars are forced to 0.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, lower_shadow, real_body, upper_shadow

# TA-Lib reports a lookback of 10 for CDLDRAGONFLYDOJI (BodyDoji / ShadowVeryShort period 10).
_LOOKBACK = 10


def dragonfly_doji(df: pd.DataFrame) -> pd.Series:
    """Dragonfly Doji pattern over ``df`` (OHLC) as a -100/0/100 ``Series`` (here 0 or 100).

    Matches ``talib.CDLDRAGONFLYDOJI`` bit-exactly: 100 where the bar is a doji with a long
    lower shadow and no upper shadow, 0 elsewhere, and 0 during the 10-bar warm-up where the
    averages are undefined.
    """
    rb = real_body(df).to_numpy()
    body_doji = candle_average(df, "BodyDoji").to_numpy()
    shadow_vs = candle_average(df, "ShadowVeryShort").to_numpy()
    lower = lower_shadow(df).to_numpy()
    upper = upper_shadow(df).to_numpy()

    # NaN averages during warm-up -> comparisons are False -> 0, matching TA-Lib's lookback.
    hit = (rb <= body_doji) & (lower > shadow_vs) & (upper < shadow_vs)
    out = np.where(hit, 100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 10 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class DragonflyDoji(Indicator):
    """Dragonfly Doji candlestick pattern.

    What: a doji with a long lower shadow and no upper shadow — price was rejected lower and
    closed back at the open/high; a potential bullish reversal at the bottom of a downtrend.
    Best settings: parameterless; body is a doji (<=10% of the 10-bar range), the lower shadow
    exceeds and the upper shadow falls below the ShadowVeryShort threshold.
    Edge cases: non-directional (0 or 100); first 10 bars are 0 (TA-Lib lookback).
    Parity: TA-Lib ``CDLDRAGONFLYDOJI`` (BodyDoji + ShadowVeryShort = HighLow/10/0.1), exact.
    """

    class Params(BaseModel):
        """Parameters for Dragonfly Doji (TA-Lib ``CDLDRAGONFLYDOJI`` takes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="dragonfly_doji",
        category="candles",
        aliases=("DragonflyDoji", "CDLDRAGONFLYDOJI"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("dragonfly_doji",),
        bounds={"dragonfly_doji": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLDRAGONFLYDOJI",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return dragonfly_doji(df)
