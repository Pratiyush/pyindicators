"""CDLENGULFING — Engulfing pattern (two bars, bidirectional).

The current real body completely engulfs the previous (opposite-colour) real body. TA-Lib::

    bullish (+): white now, black prev, close >= prev_open AND open <= prev_close
    bearish (-): black now, white prev, open  >= prev_close AND close <= prev_open

with **at least one** of the two edges strictly beyond the previous body (a fully-identical
body is not an engulfing). The magnitude is 100 when *both* edges are strictly beyond, and
**80** when exactly one edge merely touches (equals) the previous body — matching TA-Lib's
partial-penetration score. Sign is the current candle's colour.

TA-Lib's lookback for this pattern is 2, so the first two bars are forced to 0.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_color

# TA-Lib reports a lookback of 2 for CDLENGULFING; the first two outputs are always 0.
_LOOKBACK = 2


def engulfing(df: pd.DataFrame) -> pd.Series:
    """Engulfing pattern over ``df`` (OHLC) as a -100/-80/0/80/100 ``Series``.

    Matches ``talib.CDLENGULFING`` bit-exactly, including the ±80 partial score when exactly
    one body edge touches the previous body. The first two bars are 0 (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    color = candle_color(df).to_numpy()
    n = len(c)
    out = np.zeros(n, dtype="float64")

    prev_o = o[:-1]
    prev_c = c[:-1]
    cur_o = o[1:]
    cur_c = c[1:]
    cur_col = color[1:]
    prev_col = color[:-1]

    # Bullish: white engulfs black.
    bull_incl = (cur_col == 1) & (prev_col == -1) & (cur_c >= prev_o) & (cur_o <= prev_c)
    bull_both = (cur_c > prev_o) & (cur_o < prev_c)
    bull_any = (cur_c > prev_o) | (cur_o < prev_c)
    # Bearish: black engulfs white.
    bear_incl = (cur_col == -1) & (prev_col == 1) & (cur_o >= prev_c) & (cur_c <= prev_o)
    bear_both = (cur_o > prev_c) & (cur_c < prev_o)
    bear_any = (cur_o > prev_c) | (cur_c < prev_o)

    body = np.zeros(n - 1, dtype="float64")
    bull = bull_incl & bull_any
    bear = bear_incl & bear_any
    body[bull] = np.where(bull_both[bull], 100.0, 80.0)
    body[bear] = np.where(bear_both[bear], -100.0, -80.0)
    out[1:] = body

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first two bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class Engulfing(Indicator):
    """Engulfing candlestick pattern.

    What: the current body engulfs the prior opposite-colour body — a reversal signal.
    Best settings: parameterless; bullish when white engulfs black, bearish vice versa.
    Edge cases: ±80 when exactly one edge touches the prior body; first two bars are 0.
    Parity: TA-Lib ``CDLENGULFING`` (including the ±80 partial-penetration score), exact.
    """

    spec = IndicatorSpec(
        name="engulfing",
        category="candles",
        aliases=("Engulfing", "CDLENGULFING"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("engulfing",),
        bounds={"engulfing": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLENGULFING",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return engulfing(df)
