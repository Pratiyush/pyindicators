"""CDLHAMMER — Hammer candlestick (single bar, bullish-reversal, magnitude 100).

A hammer is a small-bodied candle with a long lower shadow and (almost) no upper shadow,
appearing with its body near the *prior* bar's low — a potential bottoming/reversal signal.
TA-Lib's test::

    RealBody < BodyShort average                           # small real body
    AND LowerShadow > ShadowLong average                   # long lower shadow
    AND UpperShadow < ShadowVeryShort average              # negligible upper shadow
    AND min(open, close) <= low[i-1] + Near average[i-1]   # body near the previous low

``BodyShort`` is ``(RealBody, 10, 1.0)``, ``ShadowLong`` is ``(RealBody, 0, 1.0)`` (period 0,
so the threshold is just the bar's own real body — no warm-up), ``ShadowVeryShort`` is
``(HighLow, 10, 0.1)``, and ``Near`` is ``(HighLow, 5, 0.2)`` evaluated on the **previous**
bar (its 5-bar window ends at ``i-2``) and added to ``low[i-1]``.

Output is +100 where the pattern fires, else 0 — there is no bearish (-100) or partial (±80)
score (the shape is purely bullish and every comparison is a strict inequality against an
average, so a body edge never merely "ties"; verified — only 0/100 appear). TA-Lib takes no
``penetration`` parameter for this pattern (its signature is just OHLC). The lookback is 11
(the BodyShort/ShadowVeryShort period of 10 plus the one prior bar referenced via ``Near`` and
``low[i-1]``); the first 11 bars are forced to 0.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import (
    candle_average,
    lower_shadow,
    real_body,
    upper_shadow,
)

# TA-Lib reports a lookback of 11 for CDLHAMMER (BodyShort period 10 + one prior bar).
_LOOKBACK = 11


def hammer(df: pd.DataFrame) -> pd.Series:
    """Hammer pattern over ``df`` (OHLC) as a -100/0/100 ``Series`` (here 0 or 100).

    Matches ``talib.CDLHAMMER`` bit-exactly: 100 where the real body is short, the lower shadow
    long, the upper shadow negligible, and the body sits near the previous bar's low; 0
    elsewhere. The first 11 bars are 0 (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    low = df[LOW].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    body_short = candle_average(df, "BodyShort").to_numpy()
    shadow_long = candle_average(df, "ShadowLong").to_numpy()
    very_short = candle_average(df, "ShadowVeryShort").to_numpy()
    near = candle_average(df, "Near").to_numpy()
    upper = upper_shadow(df).to_numpy()
    lower = lower_shadow(df).to_numpy()
    n = len(c)

    # ``Near`` and ``low`` are referenced on the previous bar (i-1); shift them forward so
    # position i holds the prior-bar value. The leading slot stays NaN -> comparison False.
    near_prev = np.full(n, np.nan)
    near_prev[1:] = near[:-1]
    low_prev = np.full(n, np.nan)
    low_prev[1:] = low[:-1]
    body_lo = np.minimum(o, c)

    hit = (
        (rb < body_short)
        & (lower > shadow_long)
        & (upper < very_short)
        & (body_lo <= low_prev + near_prev)
    )  # NaN averages during warm-up -> False -> 0

    out = np.where(hit, 100.0, 0.0)
    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 11 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class Hammer(Indicator):
    """Hammer candlestick pattern.

    What: a small body with a long lower shadow and no upper shadow, near the prior low — a
    bullish-reversal signal after a decline.
    Best settings: parameterless; short body, lower shadow > average body, upper shadow < 10%
    of the average range, body within 20% of the average range above the previous low.
    Edge cases: first 11 bars are 0; output is only 0 or 100 (no bearish/partial score).
    Parity: TA-Lib ``CDLHAMMER`` (BodyShort = RealBody/10/1.0, ShadowLong = RealBody/0/1.0,
    ShadowVeryShort = HighLow/10/0.1, Near = HighLow/5/0.2 on the prior bar), exact integer
    match.
    """

    spec = IndicatorSpec(
        name="hammer",
        category="candles",
        aliases=("Hammer", "CDLHAMMER"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("hammer",),
        bounds={"hammer": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLHAMMER",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return hammer(df)
