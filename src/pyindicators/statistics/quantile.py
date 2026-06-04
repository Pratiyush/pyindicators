"""Rolling Quantile — a configurable rolling percentile (statistics)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def quantile(close: pd.Series, length: int = 30, q: float = 0.5) -> pd.Series:
    """Rolling ``q``-quantile of ``close`` over ``length`` bars."""
    return close.rolling(length, min_periods=length).quantile(q)


@INDICATORS.register
class Quantile(Indicator):
    """Rolling Quantile.

    What: the ``q``-th quantile over ``length`` bars (q=0.5 is the median).
    Best settings: ``length`` 30, ``q`` 0.5.
    Edge cases: first ``length-1`` bars NaN.
    Parity: pandas-ta ``quantile``.
    """

    spec = IndicatorSpec(
        name="quantile",
        category="statistics",
        aliases=("Rolling Quantile",),
        inputs=(CLOSE,),
        outputs=("quantile",),
        references=("pandas-ta quantile",),
        doc="ref/ta_docs/statistics/misc_statistics.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=30, ge=1)
        q: float = Field(default=0.5, ge=0.0, le=1.0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return quantile(df[CLOSE], self.params["length"], self.params["q"])
