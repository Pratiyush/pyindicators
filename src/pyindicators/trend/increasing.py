"""Increasing — 1 when price is higher than ``length`` bars ago, else 0."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def increasing(close: pd.Series, length: int = 1) -> pd.Series:
    """1.0 where close > close ``length`` bars ago, else 0.0."""
    return (close.diff(length) > 0).astype("float64")


@INDICATORS.register
class Increasing(Indicator):
    """Increasing.

    What: a 0/1 flag for whether price has risen over ``length`` bars.
    Best settings: ``length`` 1.
    Edge cases: the first ``length`` bars have no prior reference (treated as 0).
    Parity: pandas-ta ``increasing``.
    """

    spec = IndicatorSpec(
        name="increasing",
        category="trend",
        aliases=("Increasing",),
        inputs=(CLOSE,),
        outputs=("increasing",),
        bounds={"increasing": (0.0, 1.0)},
        references=("pandas-ta increasing",),
        doc="ref/ta_docs/trend/README.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=1, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return increasing(df[CLOSE], self.params["length"])
