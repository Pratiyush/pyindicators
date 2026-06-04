"""CDLDARKCLOUDCOVER — Dark Cloud Cover (two bars, bearish reversal).

A long white candle is followed by a black candle that gaps up (opens above the prior high)
yet closes back *into* — but not below — the prior white body, past a penetration threshold.
A bearish top-reversal signal. TA-Lib::

    color(prev) == white                                  # 1st: long white candle
    AND RealBody(prev) > BodyLong average(prev)
    AND color(cur) == black                                # 2nd: black candle
    AND open(cur)  > high(prev)                            # gaps above the prior high
    AND close(cur) > open(prev)                            # still closes within the prior body
    AND close(cur) < close(prev) - RealBody(prev) * penetration   # deep into the body

Output is 0 or **-100** (purely bearish; no bullish or partial-penetration score). The
``penetration`` factor defaults to TA-Lib's 0.5 (how far below the prior close the black
candle must close, as a fraction of the prior real body).

``BodyLong`` is ``(RealBody, 10, 1.0)``; the previous body's long-body average needs 10 prior
bars, so TA-Lib's lookback is 11 (the first 11 bars are 0).
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, candle_color, real_body

# TA-Lib reports a lookback of 11 for CDLDARKCLOUDCOVER (BodyLong period 10 on the prev bar).
_LOOKBACK = 11

# TA-Lib's default penetration for CDLDARKCLOUDCOVER.
_DEFAULT_PENETRATION = 0.5


def dark_cloud_cover(df: pd.DataFrame, penetration: float = _DEFAULT_PENETRATION) -> pd.Series:
    """Dark Cloud Cover over ``df`` (OHLC) as a 0/-100 ``Series``.

    Matches ``talib.CDLDARKCLOUDCOVER`` bit-exactly: -100 where a long white candle is
    followed by a black candle that gaps above the prior high but closes more than
    ``penetration`` of the prior body below the prior close (while staying above the prior
    open), else 0. The first 11 bars are 0 (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    h = df[HIGH].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    rb = real_body(df).to_numpy()
    body_long = candle_average(df, "BodyLong").to_numpy()
    color = candle_color(df).to_numpy()
    n = len(c)
    out = np.zeros(n, dtype="float64")

    # Previous = bars [0..n-2], current = bars [1..n-1].
    white_long_prev = (color[:-1] == 1) & (rb[:-1] > body_long[:-1])  # NaN average -> False
    black_cur = color[1:] == -1
    gap_up = o[1:] > h[:-1]
    within_body = c[1:] > o[:-1]
    deep = c[1:] < c[:-1] - rb[:-1] * penetration

    hit = white_long_prev & black_cur & gap_up & within_body & deep
    out[1:] = np.where(hit, -100.0, 0.0)

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 11 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class DarkCloudCover(Indicator):
    """Dark Cloud Cover candlestick pattern.

    What: a black candle gaps above a long white candle's high then closes deep into its
    body — a bearish top-reversal signal.
    Best settings: ``penetration`` (default 0.5) sets how far below the prior close the black
    candle must close, as a fraction of the prior real body.
    Edge cases: output is only 0 or -100 (no bullish/partial score); first 11 bars are 0.
    Parity: TA-Lib ``CDLDARKCLOUDCOVER`` (BodyLong = RealBody/10/1.0, penetration 0.5), exact.
    """

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="dark_cloud_cover",
        category="candles",
        aliases=("DarkCloudCover", "CDLDARKCLOUDCOVER"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("dark_cloud_cover",),
        bounds={"dark_cloud_cover": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLDARKCLOUDCOVER",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        penetration: float = Field(
            default=_DEFAULT_PENETRATION,
            ge=0.0,
            description="Fraction of the prior real body the black candle must close below "
            "the prior close (TA-Lib default 0.5).",
        )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return dark_cloud_cover(df, penetration=self.params["penetration"])
