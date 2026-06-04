"""CDLINVERTEDHAMMER — Inverted Hammer candlestick (single bar, bullish-reversal, mag 100).

An inverted hammer is the vertical mirror of the Hammer: a small-bodied candle with a long
*upper* shadow and (almost) no lower shadow, gapping **down** away from the previous bar — a
potential bottoming/reversal signal after a decline. TA-Lib's test::

    RealBody     <  BodyShort        average            # small real body
    AND UpperShadow  >  ShadowLong       average        # long upper shadow
    AND LowerShadow  <  ShadowVeryShort  average        # negligible lower shadow
    AND max(open, close) < min(open, close)[i-1]        # real body gaps DOWN from prior bar

``BodyShort`` is ``(RealBody, 10, 1.0)``, ``ShadowLong`` is ``(RealBody, 0, 1.0)`` (period 0,
so the threshold is just the bar's own real body — no warm-up), and ``ShadowVeryShort`` is
``(HighLow, 10, 0.1)``. The final clause is TA-Lib's ``TA_REALBODYGAPDOWN(i, i-1)``: the
current real body lies entirely below the previous real body. This gap-down requirement is
exactly what distinguishes the Inverted Hammer (bullish, after a downtrend) from the
otherwise-identical Shooting Star shape.

Output is +100 where the pattern fires, else 0 — there is no bearish (-100) or partial (±80)
score (the shape is purely bullish and every comparison is a strict inequality, so a body edge
never merely "ties"; verified against ``talib`` on synthetic and real bars — only 0/100
appear). TA-Lib takes no ``penetration`` parameter for this pattern (its signature is just
OHLC). The lookback is 11 (the BodyShort/ShadowVeryShort period of 10 plus the one prior bar
referenced by the gap-down clause); the first 11 bars are forced to 0.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, lower_shadow, real_body, upper_shadow

# TA-Lib reports a lookback of 11 for CDLINVERTEDHAMMER (BodyShort period 10 + one prior bar).
_LOOKBACK = 11


def inverted_hammer(df: pd.DataFrame) -> pd.Series:
    """Inverted Hammer pattern over ``df`` (OHLC) as a -100/0/100 ``Series`` (here 0 or 100).

    Matches ``talib.CDLINVERTEDHAMMER`` bit-exactly: 100 where the real body is short, the upper
    shadow long, the lower shadow negligible, and the body gaps down below the previous bar's
    body; 0 elsewhere. The first 11 bars are 0 (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    body_short = candle_average(df, "BodyShort").to_numpy()
    shadow_long = candle_average(df, "ShadowLong").to_numpy()
    very_short = candle_average(df, "ShadowVeryShort").to_numpy()
    upper = upper_shadow(df).to_numpy()
    lower = lower_shadow(df).to_numpy()
    n = len(c)

    body_hi = np.maximum(o, c)
    body_lo = np.minimum(o, c)
    # Real-body gap down vs the previous bar: max(o,c)[i] < min(o,c)[i-1]. The leading slot has
    # no prior bar -> False (and is inside the lookback anyway).
    gap_down = np.zeros(n, dtype=bool)
    gap_down[1:] = body_hi[1:] < body_lo[:-1]

    hit = (
        (rb < body_short)
        & (upper > shadow_long)
        & (lower < very_short)
        & gap_down
    )  # NaN averages during warm-up -> False -> 0

    out = np.where(hit, 100.0, 0.0)
    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 11 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class InvertedHammer(Indicator):
    """Inverted Hammer candlestick pattern.

    What: a small body with a long upper shadow and no lower shadow, gapping down from the prior
    bar — the mirror of the Hammer; a bullish-reversal signal after a decline.
    Best settings: parameterless; short body, upper shadow > average body, lower shadow < 10% of
    the average range, and the real body entirely below the previous bar's body.
    Edge cases: first 11 bars are 0; output is only 0 or 100 (no bearish/partial score).
    Parity: TA-Lib ``CDLINVERTEDHAMMER`` (BodyShort = RealBody/10/1.0, ShadowLong =
    RealBody/0/1.0, ShadowVeryShort = HighLow/10/0.1, real-body gap-down vs the prior bar),
    exact integer match.
    """

    class Params(BaseModel):
        """Parameters for Inverted Hammer (TA-Lib ``CDLINVERTEDHAMMER`` takes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="inverted_hammer",
        category="candles",
        aliases=("InvertedHammer", "CDLINVERTEDHAMMER"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("inverted_hammer",),
        bounds={"inverted_hammer": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLINVERTEDHAMMER",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return inverted_hammer(df)
