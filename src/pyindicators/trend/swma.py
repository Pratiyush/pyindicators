"""SWMA — Symmetric Weighted Moving Average (triangular symmetric weights)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from ._weighted import weighted_ma


def _symmetric_triangle(length: int) -> list[int]:
    if length % 2 == 0:
        first = list(range(1, length // 2 + 1))
        return first + first[::-1]
    first = list(range(1, (length + 1) // 2 + 1))
    return first + first[-2::-1]


def swma(close: pd.Series, length: int = 10) -> pd.Series:
    """Symmetric Weighted MA (weights rise to the window centre then fall)."""
    return weighted_ma(close, _symmetric_triangle(length))


@INDICATORS.register
class SWMA(Indicator):
    """Symmetric Weighted Moving Average.

    What: a weighted MA whose triangular weights peak at the centre of the window.
    Best settings: ``length`` 10.
    Edge cases: first ``length-1`` bars NaN.
    Parity: pandas-ta ``swma``.
    """

    spec = IndicatorSpec(
        name="swma",
        category="trend",
        aliases=("Symmetric Weighted MA",),
        inputs=(CLOSE,),
        outputs=("swma",),
        references=("pandas-ta swma",),
        doc="ref/ta_docs/trend/misc_MA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=10, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return swma(df[CLOSE], self.params["length"])
