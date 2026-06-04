"""CHOP — Choppiness Index: is the market trending or ranging? (E.W. Dreiss).

``CHOP = 100 * log10(sum(TR, N) / (HH(N) - LL(N))) / log10(N)``. High (~100) = choppy/ranging,
low (~0) = trending. Composes ``base.true_range``. See ``ref/ta_docs/trend/README.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import true_range
from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec, safe_divide


def chop(df: pd.DataFrame, length: int = 14) -> pd.Series:
    """Choppiness Index over ``length`` bars."""
    sum_tr = true_range(df).rolling(length, min_periods=length).sum()
    hh = df[HIGH].rolling(length, min_periods=length).max()
    ll = df[LOW].rolling(length, min_periods=length).min()
    return 100.0 * np.log10(safe_divide(sum_tr, hh - ll)) / np.log10(length)


@INDICATORS.register
class Choppiness(Indicator):
    """Choppiness Index.

    What: how choppy vs trending the market is (0-100); ~100 = ranging, ~0 = trending.
    Best settings: ``length`` 14 (needs >= 2 for log10(length)).
    Edge cases: flat range (HH==LL) -> guarded to NaN.
    Parity: pandas-ta ``chop``.
    """

    spec = IndicatorSpec(
        name="chop",
        category="trend",
        aliases=("Choppiness Index",),
        inputs=(HIGH, LOW, "close"),
        outputs=("chop",),
        references=("Dreiss", "pandas-ta chop"),
        doc="ref/ta_docs/trend/README.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=2)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return chop(df, self.params["length"])
