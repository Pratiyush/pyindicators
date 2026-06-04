"""MACDFIX — MACD with the fast/slow periods fixed at 12/26 (trend/momentum).

Identical math to :func:`pyindicators.trend.macd.macd` but the only configurable knob is the
signal period (TA-Lib's ``MACDFIX``): ``line = EMA(c, 12) - EMA(c, 26)``;
``signal = EMA(line, signal)``; ``hist = line - signal``. Composes ``base.ema`` so the SMA
seeding convention flows through all three outputs. See ``ref/ta_docs/trend/MACD.md``.

Parity: pandas-ta ``macd`` (default branch) is an exact oracle here — its clean per-EMA
SMA seeding equals our composition bit-for-bit. TA-Lib ``MACDFIX`` seeds the fast EMA from
the slow EMA's start rather than independently, a permanent (non-decaying) offset, so it
only agrees in *shape* (tail correlation), not absolute value.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def macdfix(close: pd.Series, signal: int = 9, talib_compatible: bool = True) -> dict:
    """Return the fixed-12/26 MACD line, signal line, and histogram.

    ``fast``/``slow`` are pinned to 12/26 by definition; only ``signal`` varies. The line is
    ``EMA(close, 12) - EMA(close, 26)``, the signal its ``signal``-period EMA, and the
    histogram their difference. EMA seeding follows ``talib_compatible`` (SMA seed by
    default), so all three outputs share one warm-up convention.
    """
    line = ema(close, 12, talib_compatible) - ema(close, 26, talib_compatible)
    signal_line = ema(line, signal, talib_compatible)
    return {
        "macdfix": line,
        "macdfix_signal": signal_line,
        "macdfix_hist": line - signal_line,
    }


@INDICATORS.register
class MACDFIX(Indicator):
    """MACD Fixed 12/26.

    What: the classic 12/26 MACD line, its signal EMA, and the histogram — with only the
        signal period left configurable (TA-Lib's ``MACDFIX``).
    Best settings: signal 9 (classic). Use plain ``macd`` when you need to tune fast/slow.
    Edge cases: meaningful only after ~26+signal bars; a constant series -> all zeros; EMA
        seeding flows identically to all three outputs.
    Parity: pandas-ta ``macd`` (exact, clean SMA-seeded EMAs); TA-Lib ``MACDFIX`` agrees in
        shape only (it seeds the fast EMA off the slow EMA's start — a fixed offset).
    """

    spec = IndicatorSpec(
        name="macdfix",
        category="trend",
        aliases=("MACD Fixed 12/26", "MACDFIX"),
        inputs=(CLOSE,),
        outputs=("macdfix", "macdfix_signal", "macdfix_hist"),
        talib_compatible=True,
        references=("Appel", "TA-Lib MACDFIX", "pandas-ta macd"),
        doc="ref/ta_docs/trend/MACD.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        signal: int = Field(default=9, ge=1)
        talib_compatible: bool = True

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return macdfix(df[CLOSE], p["signal"], p["talib_compatible"])
