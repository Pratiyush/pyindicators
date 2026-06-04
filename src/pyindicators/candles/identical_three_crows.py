"""CDLIDENTICAL3CROWS — Identical Three Crows pattern (three bars, bearish-only).

Three consecutive long-ish black candles, each closing progressively lower with a very short
lower shadow, where each candle opens *at* (within an ``Equal`` band of) the previous
candle's close — the "identical" opens that distinguish this from plain Three Black Crows. A
strong top reversal. TA-Lib::

    color(i-2) == -1 AND lower_shadow(i-2) < ShadowVeryShort avg(i-2)   # 1st black crow
    color(i-1) == -1 AND lower_shadow(i-1) < ShadowVeryShort avg(i-1)   # 2nd black crow
    color(i)   == -1 AND lower_shadow(i)   < ShadowVeryShort avg(i)     # 3rd black crow
    close(i-2) > close(i-1) AND close(i-1) > close(i)                   # progressively lower
    abs(open(i-1) - close(i-2)) <= Equal avg(i-2)   # 2nd opens at the 1st's close
    abs(open(i)   - close(i-1)) <= Equal avg(i-1)   # 3rd opens at the 2nd's close

This is a one-sided (bearish) pattern: the output is **only -100 or 0** — no bullish variant
and no ±80 partial-penetration score. ``ShadowVeryShort`` is ``(HighLow, 10, 0.1)`` and
``Equal`` is ``(HighLow, 5, 0.05)``; the binding ``ShadowVeryShort`` average on bar ``i-2``
needs 10 prior bars, so TA-Lib's lookback is 10 + 2 = 12 (the first 12 bars are 0).
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, lower_shadow

# TA-Lib reports a lookback of 12 for CDLIDENTICAL3CROWS (ShadowVeryShort period 10 + 2 bars).
_LOOKBACK = 12


def identical_three_crows(df: pd.DataFrame) -> pd.Series:
    """Identical Three Crows over ``df`` (OHLC) as a -100/0 ``Series``.

    Matches ``talib.CDLIDENTICAL3CROWS`` bit-exactly: -100 where the three-bar bearish pattern
    forms, 0 elsewhere. The first 12 bars are 0 (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    color = candle_color(df).to_numpy()
    ls = lower_shadow(df).to_numpy()
    svs = candle_average(df, "ShadowVeryShort").to_numpy()
    equal = candle_average(df, "Equal").to_numpy()
    n = len(c)
    out = np.zeros(n, dtype="float64")

    if n > _LOOKBACK:
        # Current bar i runs over [2 .. n-1]; the three crows are bars i-2, i-1, i.
        i = np.arange(2, n)
        i1 = i - 1
        i2 = i - 2

        hit = (
            (color[i2] == -1)
            & (ls[i2] < svs[i2])
            & (color[i1] == -1)
            & (ls[i1] < svs[i1])
            & (color[i] == -1)
            & (ls[i] < svs[i])
            & (c[i2] > c[i1])
            & (c[i1] > c[i])
            & (o[i1] <= c[i2] + equal[i2])
            & (o[i1] >= c[i2] - equal[i2])
            & (o[i] <= c[i1] + equal[i1])
            & (o[i] >= c[i1] - equal[i1])
        )
        out[2:] = np.where(hit, -100.0, 0.0)  # NaN ShadowVeryShort/Equal avg -> False -> 0

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 12 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class IdenticalThreeCrows(Indicator):
    """Identical Three Crows candlestick pattern.

    What: three consecutive lower-closing black candles with tiny lower shadows, each opening
    at the prior candle's close (the "identical" opens) — a strong bearish top reversal.
    Best settings: parameterless; ``ShadowVeryShort`` body threshold is 10% of the 10-bar
    range and the ``Equal`` open band is 5% of the 5-bar range.
    Edge cases: bearish-only (output is -100 or 0, never +100/±80); first 12 bars are 0.
    Parity: TA-Lib ``CDLIDENTICAL3CROWS`` (ShadowVeryShort = HighLow/10/0.1, Equal =
    HighLow/5/0.05), exact integer match.
    """

    class Params(BaseModel):
        """Parameters for Identical Three Crows (TA-Lib ``CDLIDENTICAL3CROWS`` takes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="identical_three_crows",
        category="candles",
        aliases=("IdenticalThreeCrows", "CDLIDENTICAL3CROWS"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("identical_three_crows",),
        bounds={"identical_three_crows": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLIDENTICAL3CROWS",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return identical_three_crows(df)
