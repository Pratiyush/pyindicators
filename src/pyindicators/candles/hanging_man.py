"""CDLHANGINGMAN — Hanging Man candlestick (single bar, bearish, magnitude 100).

A hanging man is a small-bodied candle with a long lower shadow and (almost) no upper shadow
— the same shape as a hammer — but it appears at the *top* of an uptrend, so TA-Lib emits it
as a bearish reversal warning (-100). The geometry::

    RealBody    < BodyShort average         # small real body
    LowerShadow > ShadowLong average         # long lower shadow (>= the real body)
    UpperShadow < ShadowVeryShort average    # no, or a very short, upper shadow

plus an **uptrend confirmation** comparing the current body to the *previous* bar — the prior
high must sit at or below the current body's bottom, within a ``Near`` tolerance::

    high[i-1] <= min(open, close)[i] + Near average(i-1)

i.e. the candle opened near / above the prior session's high (a rising market). ``BodyShort``
is ``(RealBody, 10, 1.0)``, ``ShadowLong`` is ``(RealBody, 0, 1.0)``, ``ShadowVeryShort`` is
``(HighLow, 10, 0.1)`` and ``Near`` is ``(HighLow, 5, 0.2)``. The ``Near`` average is anchored
at the *previous* bar (the window ending at ``i-2``), which — together with the one-bar trend
reference — is why TA-Lib's lookback is 11 (the ``BodyShort`` period of 10 plus one prior bar).

Output is -100 for a hanging man, else 0. There is no +100 case (it is a bearish-only signal)
and no partial-penetration (±80) score: the comparison that can tie is ``<=`` against the
``Near`` average, which is folded into the -100/0 decision (verified bit-exact against
``talib.CDLHANGINGMAN`` on synthetic, real AAPL, and 100k random bars). TA-Lib takes no
``penetration`` parameter for this pattern. The first 11 bars are forced to 0 (TA-Lib lookback).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, lower_shadow, real_body, upper_shadow

# TA-Lib reports a lookback of 11 for CDLHANGINGMAN (BodyShort period 10 plus one prior bar).
_LOOKBACK = 11


def hanging_man(df: pd.DataFrame) -> pd.Series:
    """Hanging Man pattern over ``df`` (OHLC) as a -100/0 ``Series``.

    Matches ``talib.CDLHANGINGMAN`` bit-exactly: a hammer-shaped bar (small body, long lower
    shadow, very short upper shadow) whose body opened near or above the prior bar's high
    (``high[i-1] <= min(open, close)[i] + Near average(i-1)``) — the uptrend that turns the
    hammer shape into a bearish hanging man. The first 11 bars are 0 (TA-Lib lookback).
    """
    rb = real_body(df).to_numpy()
    upper = upper_shadow(df).to_numpy()
    lower = lower_shadow(df).to_numpy()
    body_short = candle_average(df, "BodyShort").to_numpy()
    shadow_long = candle_average(df, "ShadowLong").to_numpy()
    very_short = candle_average(df, "ShadowVeryShort").to_numpy()
    # ``Near`` anchored at the previous bar (its window ends at i-2): shift the i-anchored avg.
    near_prev = candle_average(df, "Near").shift(1).to_numpy()

    body_lo = np.minimum(df[OPEN].to_numpy(), df[CLOSE].to_numpy())
    n = len(rb)
    prev_high = np.empty(n, dtype="float64")
    prev_high[0] = np.nan
    prev_high[1:] = df[HIGH].to_numpy()[:-1]

    # NaN averages (warm-up) propagate to False, so those bars stay 0.
    shape = (rb < body_short) & (lower > shadow_long) & (upper < very_short)
    uptrend = prev_high <= body_lo + near_prev
    hit = shape & uptrend

    out = np.where(hit, -100.0, 0.0)
    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 11 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class HangingMan(Indicator):
    """Hanging Man candlestick.

    What: a small body with a long lower shadow and no upper shadow (a hammer shape) appearing
    after an uptrend — a bearish reversal warning.
    Best settings: parameterless; body < 10-bar average body, lower shadow > the real body,
    upper shadow < 10% of the average range, and the prior high within a ``Near`` tolerance of
    the current body bottom (the rising-market confirmation).
    Edge cases: first 11 bars are 0; output is -100 (bearish) or 0 only — no +100, no ±80 score.
    Parity: TA-Lib ``CDLHANGINGMAN`` (BodyShort = RealBody/10/1.0, ShadowLong = RealBody/0/1.0,
    ShadowVeryShort = HighLow/10/0.1, Near = HighLow/5/0.2 anchored at the prior bar), exact.
    """

    spec = IndicatorSpec(
        name="hanging_man",
        category="candles",
        aliases=("Hanging Man", "CDLHANGINGMAN"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("hanging_man",),
        bounds={"hanging_man": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLHANGINGMAN",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    class Params(BaseModel):
        # CDLHANGINGMAN takes no parameters; forbid stray kwargs and stay immutable.
        model_config = ConfigDict(extra="forbid", frozen=True)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return hanging_man(df)
