"""Decreasing — 1 when price is lower than ``length`` bars ago, else 0."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def decreasing(close: pd.Series, length: int = 1) -> pd.Series:
    """1.0 where close < close ``length`` bars ago, else 0.0."""
    return (close.diff(length) < 0).astype("float64")


@INDICATORS.register
class Decreasing(Indicator):
    """Decreasing.

    What: a 0/1 flag for whether price has fallen over ``length`` bars.
    Best settings: ``length`` 1.
    Edge cases: the first ``length`` bars have no prior reference (treated as 0).
    Parity: pandas-ta ``decreasing``.
    """

    spec = IndicatorSpec(
        name="decreasing",
        category="trend",
        aliases=("Decreasing",),
        inputs=(CLOSE,),
        outputs=("decreasing",),
        bounds={"decreasing": (0.0, 1.0)},
        references=("pandas-ta decreasing",),
        doc="ref/ta_docs/trend/README.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=1, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return decreasing(df[CLOSE], self.params["length"])
