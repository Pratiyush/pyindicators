"""PWMA — Pascal's Weighted Moving Average (weights = a row of Pascal's triangle)."""

from __future__ import annotations

from math import comb

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from ._weighted import weighted_ma


def _pascal_row(n: int) -> list[int]:
    return [comb(n - 1, k) for k in range(n)]


def pwma(close: pd.Series, length: int = 10) -> pd.Series:
    """Pascal's Weighted MA (binomial-coefficient weights)."""
    return weighted_ma(close, _pascal_row(length))


@INDICATORS.register
class PWMA(Indicator):
    """Pascal's Weighted Moving Average.

    What: a weighted MA whose weights are a row of Pascal's triangle (binomial, bell-shaped).
    Best settings: ``length`` 10.
    Edge cases: first ``length-1`` bars NaN.
    Parity: pandas-ta ``pwma``.
    """

    spec = IndicatorSpec(
        name="pwma",
        category="trend",
        aliases=("Pascal Weighted MA",),
        inputs=(CLOSE,),
        outputs=("pwma",),
        references=("pandas-ta pwma",),
        doc="ref/ta_docs/trend/misc_MA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=10, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return pwma(df[CLOSE], self.params["length"])
