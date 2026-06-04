"""CDLXSIDEGAP3METHODS — Upside/Downside gap three methods (three bars, bidirectional).

A continuation pattern that "fills" a gap. Two candles of the **same** colour leave a gap
between them; a third candle of the **opposite** colour opens inside the second body and closes
inside the first body, partially closing the gap — the trend then resumes. TA-Lib::

    color(i-2) == color(i-1)                       # 1st and 2nd same colour
    AND color(i-1) == -color(i)                     # 3rd is the opposite colour
    AND open(i)  < max(open, close)[i-1]            # 3rd opens within the 2nd body ...
    AND open(i)  > min(open, close)[i-1]
    AND close(i) < max(open, close)[i-2]            # ... and closes within the 1st body
    AND close(i) > min(open, close)[i-2]
    AND ( ( color(i-1) == white                     # upside gap (white 1st/2nd):
            AND min(open, close)[i-1] > max(open, close)[i-2] )   # 2nd body above 1st
       OR ( color(i-1) == black                     # downside gap (black 1st/2nd):
            AND max(open, close)[i-1] < min(open, close)[i-2] ) ) # 2nd body below 1st

Output is ``color(i-1) * 100``: +100 for an upside gap (white candles, bullish continuation)
and -100 for a downside gap (black candles, bearish continuation), 0 otherwise. This is a pure
±100 / 0 signal — every condition is a strict geometric inequality, so TA-Lib emits **no** ±80
partial-penetration score for this pattern.

The pattern uses no candle-setting averages (purely the three bodies' geometry), so TA-Lib's
lookback is just 2 — the first two bars are forced to 0.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_color

# TA-Lib reports a lookback of 2 for CDLXSIDEGAP3METHODS (it spans 3 bars, no averages);
# the first two outputs are always 0.
_LOOKBACK = 2


def xside_gap_three_methods(df: pd.DataFrame) -> pd.Series:
    """Upside/Downside gap three methods over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDLXSIDEGAP3METHODS`` bit-exactly: +100 on an upside gap (two white
    candles), -100 on a downside gap (two black candles), when the opposite-colour third candle
    opens inside the second body and closes inside the first body. The first two bars are 0
    (TA-Lib lookback). Output is pure ±100/0 — there is no partial ±80 score for this pattern.
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    color = candle_color(df).to_numpy()
    body_hi = np.maximum(o, c)
    body_lo = np.minimum(o, c)
    n = len(c)
    out = np.zeros(n, dtype="float64")

    # Output at i spans three candles: i-2 (1st), i-1 (2nd), i (3rd / current).
    one = slice(0, n - 2)
    two = slice(1, n - 1)
    cur = slice(2, n)
    color1 = color[one]
    color2 = color[two]
    color3 = color[cur]

    same_first_two = color1 == color2
    third_opposite = color2 == -color3
    opens_in_second = (o[cur] < body_hi[two]) & (o[cur] > body_lo[two])
    closes_in_first = (c[cur] < body_hi[one]) & (c[cur] > body_lo[one])
    gap_up = (color2 == 1) & (body_lo[two] > body_hi[one])  # white 2nd body above the 1st
    gap_down = (color2 == -1) & (body_hi[two] < body_lo[one])  # black 2nd body below the 1st

    hit = (
        same_first_two
        & third_opposite
        & opens_in_second
        & closes_in_first
        & (gap_up | gap_down)
    )
    out[2:] = np.where(hit, color2 * 100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first two bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class XSideGapThreeMethods(Indicator):
    """Upside/Downside gap three methods candlestick pattern.

    What: two same-colour candles leave a gap; an opposite-colour third candle opens inside the
    second body and closes inside the first, partially filling the gap — a continuation signal
    (bullish on an upside gap of white candles, bearish on a downside gap of black candles).
    Best settings: parameterless; purely the three bodies' geometry (no candle-setting average).
    Edge cases: pure ±100/0 (no ±80 partial score); first two bars are 0 (TA-Lib lookback).
    Parity: TA-Lib ``CDLXSIDEGAP3METHODS``, exact integer match.
    """

    class Params(BaseModel):
        """Parameters for Upside/Downside gap three methods (``CDLXSIDEGAP3METHODS`` takes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="xside_gap_three_methods",
        category="candles",
        aliases=("XSideGapThreeMethods", "CDLXSIDEGAP3METHODS"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("xside_gap_three_methods",),
        bounds={"xside_gap_three_methods": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLXSIDEGAP3METHODS",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return xside_gap_three_methods(df)
