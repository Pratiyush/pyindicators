"""CDLGAPSIDESIDEWHITE — Up/Down-gap side-by-side white lines (three bars, bidirectional).

Two same-size white candles opening at (roughly) the same level, both sitting on the *same
side* of a gap left by the candle before them — a continuation pattern. TA-Lib::

    # gap (between the pre-gap candle i-2 and the first white i-1)
    upside   gap: min(open, close)[i-1] > max(open, close)[i-2]
    downside gap: max(open, close)[i-1] < min(open, close)[i-2]
    AND color(i-1) == white AND color(i) == white          # both lines white
    AND |RealBody(i) - RealBody(i-1)| <= Near average(i-1)  # ~same body size
    AND |open(i) - open(i-1)|         <= Equal average(i-1)  # ~same open

Output is +100 on an upside gap (bullish continuation) and -100 on a downside gap (bearish
continuation), 0 otherwise. This is a pure ±100 / 0 signal: every condition is a tolerance
band (``Near``/``Equal``), so TA-Lib emits **no** ±80 partial-penetration score here.

``Near`` is ``(HighLow, 5, 0.2)`` and ``Equal`` is ``(HighLow, 5, 0.05)``; both averages are
read at the first white candle ``i-1`` (window ending at ``i-2``). TA-Lib's lookback is
``max(Near=5, Equal=5) + 2 = 7`` — the ``+2`` from the two prior candles the pattern spans —
so the first 7 bars are forced to 0.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body

# TA-Lib reports a lookback of 7 for CDLGAPSIDESIDEWHITE: max(Near=5, Equal=5) + 2, the +2
# from the two earlier candles the pattern spans (the gap candle i-2 and the first white i-1).
_LOOKBACK = 7


def gap_side_side_white(df: pd.DataFrame) -> pd.Series:
    """Up/Down-gap side-by-side white lines over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDLGAPSIDESIDEWHITE`` bit-exactly: +100 on an upside gap, -100 on a
    downside gap, when two same-size white candles open at ~the same level on the same side of
    the gap. The first 7 bars are 0 (TA-Lib lookback). Output is pure ±100/0 — there is no
    partial ±80 score for this pattern.
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    near = candle_average(df, "Near").to_numpy()
    equal = candle_average(df, "Equal").to_numpy()
    body_hi = np.maximum(o, c)
    body_lo = np.minimum(o, c)
    color = candle_color(df).to_numpy()
    n = len(c)
    out = np.zeros(n, dtype="float64")

    # Output at i spans three candles: i-2 (pre-gap), i-1 (first white), i (second white).
    # The Near/Equal averages are read at the first white candle, i-1.
    pre = slice(0, n - 2)
    first = slice(1, n - 1)
    cur = slice(2, n)
    near1 = near[first]
    equal1 = equal[first]

    gap_up = body_lo[first] > body_hi[pre]  # second-candle body wholly above the pre-gap body
    gap_down = body_hi[first] < body_lo[pre]  # ... or wholly below it
    both_white = (color[first] == 1) & (color[cur] == 1)
    same_size = (rb[cur] >= rb[first] - near1) & (rb[cur] <= rb[first] + near1)
    same_open = (o[cur] >= o[first] - equal1) & (o[cur] <= o[first] + equal1)

    common = both_white & same_size & same_open  # NaN average -> False during warm-up
    hit = (gap_up | gap_down) & common
    out[2:] = np.where(hit, np.where(gap_up, 100.0, -100.0), 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 7 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class GapSideSideWhite(Indicator):
    """Up/Down-gap side-by-side white lines candlestick pattern.

    What: two same-size white candles opening at ~the same level on the same side of a prior
    gap — a continuation signal (bullish above an upside gap, bearish below a downside gap).
    Best settings: parameterless; bodies "near" equal (Near = HighLow/5/0.2) and opens "equal"
    (Equal = HighLow/5/0.05).
    Edge cases: pure ±100/0 (no ±80 partial score); first 7 bars are 0 (TA-Lib lookback).
    Parity: TA-Lib ``CDLGAPSIDESIDEWHITE`` (Near = HighLow/5/0.2, Equal = HighLow/5/0.05),
    exact integer match.
    """

    spec = IndicatorSpec(
        name="gap_side_side_white",
        category="candles",
        aliases=("GapSideSideWhite", "CDLGAPSIDESIDEWHITE"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("gap_side_side_white",),
        bounds={"gap_side_side_white": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLGAPSIDESIDEWHITE",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return gap_side_side_white(df)
