"""CDL3LINESTRIKE — Three-Line Strike (four bars, bidirectional, no partial score).

Three same-colour candles trending in one direction, then a fourth opposite-colour candle
that "strikes back" and engulfs the whole move. TA-Lib's ``CDL3LINESTRIKE``::

    color(i-3) == color(i-2) == color(i-1)          # three same-colour candles
    AND color(i) == -color(i-1)                      # opposite-colour fourth candle
    AND open(i-2) within real_body(i-3) +/- Near avg # each candle opens near the prior body
    AND open(i-1) within real_body(i-2) +/- Near avg
    AND (
        bullish: white run, close(i-1) > close(i-2) > close(i-3),     # rising closes
                 open(i) > close(i-1) AND close(i) < open(i-3)        # 4th opens above, closes below
        OR
        bearish: black run, close(i-1) < close(i-2) < close(i-3),     # falling closes
                 open(i) < close(i-1) AND close(i) > open(i-3)        # 4th opens below, closes above
    )

Output is the *run's* colour times 100: +100 for the bullish setup (a white run struck by a
black candle), -100 for the bearish setup. Unlike engulfing/harami there is no +/-80 partial
score — TA-Lib emits only ``color(i-1) * 100`` (verified bit-exact: outputs are {-100, 0, 100}).

The only sized comparison is the ``Near`` setting ``(HighLow, 5, 0.2)`` applied on the prior
bars ``i-3`` and ``i-2``; its 5-bar average is taken over the bars ending at the bar *before*
each of those, so TA-Lib's lookback is ``avgPeriod(Near) + 3 == 8`` (the first 8 bars are 0).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color

# TA-Lib lookback for CDL3LINESTRIKE is TA_CANDLEAVGPERIOD(Near) + 3 == 5 + 3 == 8.
_LOOKBACK = 8


def three_line_strike(df: pd.DataFrame) -> pd.Series:
    """Three-Line Strike over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDL3LINESTRIKE`` bit-exactly: +100 for a bullish strike (three rising
    white candles followed by a black candle that opens above and closes below the run),
    -100 for the bearish mirror, 0 otherwise. The first 8 bars are 0 (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    color = candle_color(df).to_numpy()
    near = candle_average(df, "Near").to_numpy()  # Near avg evaluated per bar (NaN warm-up)
    body_hi = np.maximum(o, c)
    body_lo = np.minimum(o, c)
    n = len(c)
    out = np.zeros(n, dtype="float64")
    if n < 4:
        return pd.Series(out, index=df.index)

    # Align each four-bar window to the current bar i in [3, n-1]:
    #   *_m3 -> bar i-3, *_m2 -> bar i-2, *_m1 -> bar i-1, *_i -> bar i.
    col_i, col_m1, col_m2, col_m3 = color[3:], color[2:-1], color[1:-2], color[:-3]
    near_m3, near_m2 = near[:-3], near[1:-2]  # Near average evaluated at bars i-3 and i-2
    o_i, o_m1, o_m2, o_m3 = o[3:], o[2:-1], o[1:-2], o[:-3]
    c_i, c_m1, c_m2, c_m3 = c[3:], c[2:-1], c[1:-2], c[:-3]
    body_lo_m2, body_hi_m2 = body_lo[1:-2], body_hi[1:-2]
    body_lo_m3, body_hi_m3 = body_lo[:-3], body_hi[:-3]

    valid = ~np.isnan(near_m3) & ~np.isnan(near_m2)  # warm-up -> no pattern
    same_run = (col_m3 == col_m2) & (col_m2 == col_m1) & (col_i == -col_m1)
    near_ok = (
        (o_m2 >= body_lo_m3 - near_m3)
        & (o_m2 <= body_hi_m3 + near_m3)
        & (o_m1 >= body_lo_m2 - near_m2)
        & (o_m1 <= body_hi_m2 + near_m2)
    )
    bullish = (
        (col_m1 == 1) & (c_m1 > c_m2) & (c_m2 > c_m3) & (o_i > c_m1) & (c_i < o_m3)
    )
    bearish = (
        (col_m1 == -1) & (c_m1 < c_m2) & (c_m2 < c_m3) & (o_i < c_m1) & (c_i > o_m3)
    )

    hit = valid & same_run & near_ok & (bullish | bearish)
    out[3:] = np.where(hit, col_m1 * 100.0, 0.0)  # sign is the run's colour

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 8 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class ThreeLineStrike(Indicator):
    """Three-Line Strike candlestick pattern.

    What: three same-colour candles trending one way, then a fourth opposite-colour candle
    that engulfs the whole run — a (counter-intuitively continuation-biased) reversal shape.
    Best settings: parameterless; +100 for a white run struck by a black candle, -100 mirror.
    Edge cases: no +/-80 partial score (only color*100); first 8 bars are 0 (TA-Lib lookback).
    Parity: TA-Lib ``CDL3LINESTRIKE`` (Near = HighLow/5/0.2 on bars i-3, i-2), exact integer.
    """

    class Params(BaseModel):
        """CDL3LINESTRIKE takes no parameters (TA-Lib exposes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec = IndicatorSpec(
        name="three_line_strike",
        category="candles",
        aliases=("ThreeLineStrike", "CDL3LINESTRIKE"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("three_line_strike",),
        bounds={"three_line_strike": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDL3LINESTRIKE",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return three_line_strike(df)
