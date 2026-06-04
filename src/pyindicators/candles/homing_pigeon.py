"""CDLHOMINGPIGEON — Homing Pigeon pattern (two bars, bullish only).

A bullish reversal in a downtrend formed by two black candles where the second is a small
"homing pigeon" sheltering inside the first's long body — a harami-style contraction with both
bodies the same (black) colour. TA-Lib's ``CDLHOMINGPIGEON``::

    1st candle: black AND RealBody(1st) > BodyLong average(1st)     # long black
    2nd candle: black AND RealBody(2nd) <= BodyShort average(2nd)   # short black
                AND open(2nd) < open(1st)                           # 2nd opens below 1st open
                AND close(2nd) > close(1st)                         # 2nd closes above 1st close

i.e. the second body sits inside the first body. Note TA-Lib uses **open/close** containment
(not high/low) and that the second-body test is ``<=`` (a tie passes), while the first-body and
the two containment edges are strict ``>``/``<``. There is no partial-penetration score: the
output is only +100 (the pattern is bullish only) or 0 — never -100 and never the ±80 score.

Both ``BodyLong`` and ``BodyShort`` are ``(RealBody, 10, 1.0)`` with averaging period 10;
TA-Lib's lookback is ``max(10, 10) + 1 = 11`` (the long-body average is read on the previous
bar), so the first 11 bars are forced to 0.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body

# TA-Lib reports a lookback of max(BodyShort, BodyLong) avg period + 1 = 10 + 1 = 11.
_LOOKBACK = 11


def homing_pigeon(df: pd.DataFrame) -> pd.Series:
    """Homing Pigeon pattern over ``df`` (OHLC) as a -100/0/100 ``Series`` (here 0 or 100).

    Matches ``talib.CDLHOMINGPIGEON`` bit-exactly: +100 at the second bar of a Homing Pigeon
    formation (two black candles, the second's small body inside the first's long body), 0
    elsewhere. The output is pure 0/+100 (bullish only — no -100, no ±80 partial score). The
    first 11 bars are 0 (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    body_short = candle_average(df, "BodyShort").to_numpy()
    color = candle_color(df).to_numpy()
    n = len(c)
    out = np.zeros(n, dtype="float64")

    # Pair (1st, 2nd) = bars (i-1, i) for i in [1 .. n-1].
    first_black = color[:-1] == -1
    second_black = color[1:] == -1
    first_long = rb[:-1] > body_long[:-1]  # NaN average -> False during warm-up
    second_short = rb[1:] <= body_short[1:]  # TA-Lib uses <= here (a tie passes)
    open_lower = o[1:] < o[:-1]
    close_higher = c[1:] > c[:-1]

    hit = first_black & second_black & first_long & second_short & open_lower & close_higher
    out[1:] = np.where(hit, 100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 11 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class HomingPigeon(Indicator):
    """Homing Pigeon candlestick pattern.

    What: two black candles where the second's small body is sheltered inside the first's long
        body — a bullish reversal hint after a decline (a same-colour harami).
    Best settings: parameterless; the signal is bullish only (+100) or absent (0).
    Edge cases: containment uses open/close with strict edges but the short-body test is ``<=``;
        first 11 bars are 0 (TA-Lib lookback = max(BodyLong, BodyShort) period 10 + 1).
    Parity: TA-Lib ``CDLHOMINGPIGEON`` (BodyLong/BodyShort = RealBody/10/1.0), exact integer
        match — pure 0/+100, no ±80 partial-penetration score.
    """

    class Params(BaseModel):
        """Parameters for Homing Pigeon (TA-Lib ``CDLHOMINGPIGEON`` takes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="homing_pigeon",
        category="candles",
        aliases=("HomingPigeon", "CDLHOMINGPIGEON"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("homing_pigeon",),
        bounds={"homing_pigeon": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLHOMINGPIGEON",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return homing_pigeon(df)
