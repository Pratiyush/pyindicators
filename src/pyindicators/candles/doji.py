"""CDLDOJI — Doji candlestick (single bar, non-directional).

A doji is a bar whose real body is negligible relative to the recent range: open and close
are (almost) equal. TA-Lib's test is ``RealBody <= BodyDoji average`` where ``BodyDoji`` is
the ``(HighLow, 10, 0.1)`` setting — i.e. the body is at most 10% of the average ``high-low``
range over the prior 10 bars. Output is 0 or 100 (no bullish/bearish direction).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average, real_body


def doji(df: pd.DataFrame) -> pd.Series:
    """Doji pattern over ``df`` (OHLC) as a -100/0/100 ``Series`` (here 0 or 100).

    Matches ``talib.CDLDOJI`` bit-exactly: 100 where ``real_body <= candle_average(BodyDoji)``,
    0 elsewhere, and 0 during the 10-bar warm-up where the average is undefined.
    """
    rb = real_body(df)
    thr = candle_average(df, "BodyDoji")
    hit = rb <= thr  # NaN threshold -> False -> 0 during warm-up
    return pd.Series(np.where(hit, 100.0, 0.0), index=df.index)


@INDICATORS.register
class Doji(Indicator):
    """Doji candlestick.

    What: a single bar with a negligible real body (open ~ close) — market indecision.
    Best settings: parameterless; body threshold is 10% of the average 10-bar range.
    Edge cases: first 10 bars are 0 (TA-Lib lookback); ``open == close`` is always a doji.
    Parity: TA-Lib ``CDLDOJI`` (BodyDoji = HighLow/10/0.1), exact integer match.
    """

    spec = IndicatorSpec(
        name="doji",
        category="candles",
        aliases=("Doji", "CDLDOJI"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("doji",),
        bounds={"doji": (-100.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib CDLDOJI",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return doji(df)
