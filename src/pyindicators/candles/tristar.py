"""CDLTRISTAR — Tristar pattern (three bars, bidirectional).

Three consecutive doji bars, the middle one gapping away from its neighbours. TA-Lib::

    RealBody(i-2) <= BodyDoji average      # three dojis in a row, all measured against
    RealBody(i-1) <= BodyDoji average      #   the SAME average evaluated at bar i-2
    RealBody(i)   <= BodyDoji average      #   (window ending at i-3)
    AND one of:
      bearish (-): RealBody(i-1) gaps UP  from i-2 (body fully above) AND High(i) < High(i-1)
      bullish (+): RealBody(i-1) gaps DOWN from i-2 (body fully below) AND Low(i)  > Low(i-1)

A "gap up" means the *whole* real body of the middle doji sits strictly above the first
doji's body (``min(open,close)[i-1] > max(open,close)[i-2]``); "gap down" is the mirror. The
sign is set by the gap direction of the middle bar, not the candle colours. Output is the
plain ``{-100, 0, 100}`` integer set — CDLTRISTAR has no partial-penetration (±80) score and
takes no parameters.

``BodyDoji`` is the ``(HighLow, 10, 0.1)`` setting, so the doji average needs 10 prior bars
ending at ``i-3``; combined with the two-bar back-reference TA-Lib's lookback is 12 (the first
12 bars are always 0).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, real_body

# TA-Lib lookback for CDLTRISTAR: BodyDoji period (10) measured at bar i-2 -> 10 + 2 = 12.
_LOOKBACK = 12


def tristar(df: pd.DataFrame) -> pd.Series:
    """Tristar pattern over ``df`` (OHLC) as a -100/0/100 ``Series``.

    Matches ``talib.CDLTRISTAR`` bit-exactly: +100 when the three dojis bracket a downward
    gap that the third bar fails to extend, -100 for the upward-gap mirror, 0 otherwise. The
    first 12 bars are 0 (TA-Lib lookback).
    """
    o = df[OPEN].to_numpy(dtype="float64")
    h = df[HIGH].to_numpy(dtype="float64")
    low = df[LOW].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    n = len(c)
    out = np.zeros(n, dtype="float64")
    if n <= _LOOKBACK:
        return pd.Series(out, index=df.index)

    rb = real_body(df).to_numpy()
    body_doji = candle_average(df, "BodyDoji").to_numpy()
    body_hi = np.maximum(o, c)
    body_lo = np.minimum(o, c)

    # i runs over 2..n-1; align by slicing. The doji average is read at i-2 for all three
    # bodies (TA-Lib carries a single BodyPeriodTotal evaluated at i-2).
    avg = body_doji[:-2]  # average at bar i-2 (NaN during warm-up -> comparisons are False)
    three_doji = (rb[:-2] <= avg) & (rb[1:-1] <= avg) & (rb[2:] <= avg)

    gap_up = body_lo[1:-1] > body_hi[:-2]  # middle body strictly above the first body
    gap_down = body_hi[1:-1] < body_lo[:-2]  # middle body strictly below the first body

    bearish = three_doji & gap_up & (h[2:] < h[1:-1])
    bullish = three_doji & gap_down & (low[2:] > low[1:-1])

    seg = np.zeros(n - 2, dtype="float64")
    seg[bearish] = -100.0
    seg[bullish] = 100.0  # gap_up and gap_down are mutually exclusive; order is irrelevant
    out[2:] = seg

    out[:_LOOKBACK] = 0.0  # TA-Lib lookback: first 12 bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class Tristar(Indicator):
    """Tristar candlestick pattern.

    What: three consecutive dojis with the middle one gapping away — a reversal signal.
    Best settings: parameterless; bullish on a downward middle gap, bearish on an upward one.
    Edge cases: only ``{-100, 0, 100}`` (no ±80 partial); first 12 bars are 0.
    Parity: TA-Lib ``CDLTRISTAR`` (BodyDoji = HighLow/10/0.1), exact integer match.
    """

    spec = IndicatorSpec(
        name="tristar",
        category="candles",
        aliases=("Tristar", "CDLTRISTAR"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("tristar",),
        bounds={"tristar": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLTRISTAR",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return tristar(df)
