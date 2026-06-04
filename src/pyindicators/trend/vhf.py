"""VHF — Vertical Horizontal Filter: trend strength vs noise (Adam White).

``VHF = |HH(N) - LL(N)| / sum(|close - close_{t-1}|, N)``. Higher = stronger trend.
See ``ref/ta_docs/trend/README.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide


def vhf(close: pd.Series, length: int = 28) -> pd.Series:
    """Vertical Horizontal Filter over ``length`` bars."""
    hh = close.rolling(length, min_periods=length).max()
    ll = close.rolling(length, min_periods=length).min()
    numerator = (hh - ll).abs()
    denominator = close.diff().abs().rolling(length, min_periods=length).sum()
    return safe_divide(numerator, denominator)


@INDICATORS.register
class VHF(Indicator):
    """Vertical Horizontal Filter.

    What: net price range over total movement — high = trending, low = ranging.
    Best settings: ``length`` 28.
    Edge cases: zero total movement (flat) -> guarded to NaN.
    Parity: pandas-ta ``vhf``.
    """

    spec = IndicatorSpec(
        name="vhf",
        category="trend",
        aliases=("Vertical Horizontal Filter",),
        inputs=(CLOSE,),
        outputs=("vhf",),
        references=("Adam White", "pandas-ta vhf"),
        doc="ref/ta_docs/trend/README.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=28, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return vhf(df[CLOSE], self.params["length"])
