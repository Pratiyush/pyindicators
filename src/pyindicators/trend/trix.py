"""TRIX — Triple Exponential Average rate-of-change (Jack Hutson 1980s).

The 1-bar percent change of a triple-smoothed EMA: a slow, noise-filtered momentum
oscillator centred on zero. ``TRIX = 100 * (e3_t - e3_{t-1}) / e3_{t-1}`` where e3 is the
triple EMA; signal = EMA(TRIX). Composes ``base.ema``. See ``ref/ta_docs/trend/TRIX.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide


def trix(close: pd.Series, length: int = 15, signal: int = 9, talib_compatible: bool = True) -> dict:
    """TRIX line (percent ROC of triple EMA) and its signal line."""
    e3 = ema(ema(ema(close, length, talib_compatible), length, talib_compatible), length, talib_compatible)
    line = 100.0 * safe_divide(e3 - e3.shift(1), e3.shift(1))
    return {"trix": line, "trix_signal": ema(line, signal, talib_compatible)}


@INDICATORS.register
class TRIX(Indicator):
    """TRIX.

    What: percent rate of change of a triple EMA — a smooth, zero-centred momentum line.
    Best settings: ``length`` 15, signal 9; shorter length = more signals.
    Edge cases: guarded against a zero triple-EMA (degenerate data); long warm-up (~3*length).
    Parity: TA-Lib ``TRIX`` (line) / pandas-ta ``trix`` (line + signal).
    """

    spec = IndicatorSpec(
        name="trix",
        category="trend",
        aliases=("Triple Exponential Average",),
        inputs=(CLOSE,),
        outputs=("trix", "trix_signal"),
        talib_compatible=True,
        references=("Hutson", "TA-Lib TRIX", "pandas-ta trix"),
        doc="ref/ta_docs/trend/TRIX.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=15, ge=1)
        signal: int = Field(default=9, ge=1)
        talib_compatible: bool = True

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return trix(df[CLOSE], p["length"], p["signal"], p["talib_compatible"])
