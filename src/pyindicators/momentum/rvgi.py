"""RVGI — Relative Vigor Index (John Ehlers).

Measures conviction by comparing where price closes within its bar: closes tend to be near the
high in up-trends and near the low in down-trends. ``RVGI = SUM(SWMA(close-open)) /
SUM(SWMA(high-low))`` over ``length``; the signal is a 4-bar SWMA of the line. Composes
``trend.swma``. See ``ref/ta_docs/momentum/misc_momentum.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import (
    CLOSE,
    HIGH,
    INDICATORS,
    LOW,
    OPEN,
    Indicator,
    IndicatorSpec,
    safe_divide,
)
from pyindicators.trend.swma import swma


def rvgi(df: pd.DataFrame, length: int = 14, swma_length: int = 4) -> dict:
    """Relative Vigor Index line, signal, and histogram."""
    co = swma(df[CLOSE] - df[OPEN], swma_length).rolling(length, min_periods=length).sum()
    hl = swma(df[HIGH] - df[LOW], swma_length).rolling(length, min_periods=length).sum()
    line = safe_divide(co, hl)  # guarded; flat bars -> NaN
    signal = swma(line, swma_length)
    return {"rvgi": line, "rvgi_signal": signal, "rvgi_hist": line - signal}


@INDICATORS.register
class RVGI(Indicator):
    """Relative Vigor Index.

    What: trend conviction from the close-open range relative to the high-low range, SWMA-smoothed.
    Best settings: ``length`` 14, ``swma_length`` 4; RVGI/signal crossovers flag momentum shifts.
    Edge cases: zero high-low range over the window -> guarded to NaN; warm-up = length + swma.
    Parity: pandas-ta ``rvgi``, exact.
    """

    spec = IndicatorSpec(
        name="rvgi",
        category="momentum",
        aliases=("Relative Vigor Index",),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("rvgi", "rvgi_signal", "rvgi_hist"),
        references=("Ehlers", "pandas-ta rvgi"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)
        swma_length: int = Field(default=4, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        return rvgi(df, self.params["length"], self.params["swma_length"])
