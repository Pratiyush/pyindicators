"""CDLKICKING — Kicking pattern (two bars, bidirectional).

Two opposite-colour *marubozu* candles separated by a gap — a strong reversal signal that
ignores trend. TA-Lib::

    color(prev) == -color(cur)                         # opposite colours
    # both bars are marubozu (long body, negligible shadows):
    RealBody(prev) > BodyLong avg(prev)
    UpperShadow(prev) < ShadowVeryShort avg(prev)
    LowerShadow(prev) < ShadowVeryShort avg(prev)
    RealBody(cur)  > BodyLong avg(cur)
    UpperShadow(cur)  < ShadowVeryShort avg(cur)
    LowerShadow(cur)  < ShadowVeryShort avg(cur)
    # gap in the direction of the current candle:
    ( color(prev) == -1 AND Low(cur)  > High(prev) )   # black->white: bullish gap up
    OR
    ( color(prev) == +1 AND High(cur) < Low(prev)  )   # white->black: bearish gap down

Output is the current candle's colour times 100 — ``+100`` bullish (black then a gapped-up
white marubozu) or ``-100`` bearish (white then a gapped-down black marubozu); 0 otherwise.
There is no partial-penetration ``±80`` score: the gap is strict and the result is pure
``-100/0/100``.

``BodyLong`` is ``(RealBody, 10, 1.0)`` and ``ShadowVeryShort`` is ``(HighLow, 10, 0.1)``.
Both averages are needed on the *previous* bar too, so TA-Lib's lookback is 11 (the first 11
bars are 0). CDLKICKING takes no parameters.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import (
    candle_average,
    candle_color,
    lower_shadow,
    real_body,
    upper_shadow,
)

# TA-Lib reports a lookback of 11 for CDLKICKING (BodyLong/ShadowVeryShort period 10 must be
# available on the previous bar as well). The first 11 outputs are always 0.
_LOOKBACK = 11


def kicking(df: pd.DataFrame) -> pd.Series:
    """Kicking pattern over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDLKICKING`` bit-exactly: two opposite-colour marubozu candles with a
    strict gap between them, scored ``color(cur) * 100``. The first 11 bars are 0 (TA-Lib
    lookback); there is no ±80 partial score (the gap test is strict).
    """
    high = df[HIGH].to_numpy(dtype="float64")
    low = df[LOW].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    up = upper_shadow(df).to_numpy()
    lw = lower_shadow(df).to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    shadow_vs = candle_average(df, "ShadowVeryShort").to_numpy()
    color = candle_color(df).to_numpy()
    n = len(high)
    out = np.zeros(n, dtype="float64")

    if n > 1:
        # Previous = bars [0..n-2], current = bars [1..n-1].
        # A marubozu: body longer than BodyLong avg, both shadows below ShadowVeryShort avg
        # (NaN averages during warm-up propagate to False here, which the lookback also clears).
        maru_prev = (
            (rb[:-1] > body_long[:-1])
            & (up[:-1] < shadow_vs[:-1])
            & (lw[:-1] < shadow_vs[:-1])
        )
        maru_cur = (
            (rb[1:] > body_long[1:])
            & (up[1:] < shadow_vs[1:])
            & (lw[1:] < shadow_vs[1:])
        )
        opposite = color[:-1] == -color[1:]
        # Gap keyed on the previous candle's colour (current is the opposite):
        # black prev -> bullish gap up; white prev -> bearish gap down.
        gap = np.where(
            color[:-1] == -1,
            low[1:] > high[:-1],
            high[1:] < low[:-1],
        )
        hit = maru_prev & maru_cur & opposite & gap
        out[1:] = np.where(hit, color[1:] * 100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 11 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class Kicking(Indicator):
    """Kicking candlestick pattern.

    What: two opposite-colour marubozu candles with a price gap — a strong reversal signal
    that disregards the prevailing trend.
    Best settings: parameterless; bullish (+100) when a black marubozu is followed by a
    gapped-up white marubozu, bearish (-100) for the mirror image.
    Edge cases: the gap is strict (no ±80 partial score); first 11 bars are 0.
    Parity: TA-Lib ``CDLKICKING`` (BodyLong = RealBody/10/1.0, ShadowVeryShort =
    HighLow/10/0.1), exact integer match.
    """

    class Params(BaseModel):
        """Parameters for Kicking (TA-Lib ``CDLKICKING`` takes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="kicking",
        category="candles",
        aliases=("Kicking", "CDLKICKING"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("kicking",),
        bounds={"kicking": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLKICKING",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return kicking(df)
