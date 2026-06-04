"""FWMA — Fibonacci Weighted Moving Average (weights = Fibonacci sequence)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from ._weighted import weighted_ma


def _fibonacci(n: int) -> list[int]:
    a, b = 1, 1
    seq = []
    for _ in range(n):
        seq.append(a)
        a, b = b, a + b
    return seq


def fwma(close: pd.Series, length: int = 10) -> pd.Series:
    """Fibonacci Weighted MA (most recent bar gets the largest Fibonacci weight)."""
    return weighted_ma(close, _fibonacci(length))


@INDICATORS.register
class FWMA(Indicator):
    """Fibonacci Weighted Moving Average.

    What: a weighted MA whose weights follow the Fibonacci sequence.
    Best settings: ``length`` 10.
    Edge cases: first ``length-1`` bars NaN.
    Parity: pandas-ta ``fwma``.
    """

    spec = IndicatorSpec(
        name="fwma",
        category="trend",
        aliases=("Fibonacci Weighted MA",),
        inputs=(CLOSE,),
        outputs=("fwma",),
        references=("pandas-ta fwma",),
        doc="ref/ta_docs/trend/misc_MA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=10, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return fwma(df[CLOSE], self.params["length"])
