"""PDIST — Price Distance: total price movement per bar including gaps.

``PDIST = 2*(high-low) - |close-open| + |open - close_{t-1}|``. See
``ref/ta_docs/volatility/misc_volatility.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec


def pdist(df: pd.DataFrame, drift: int = 1) -> pd.Series:
    """Price Distance: 2*(H-L) - |C-O| + |O - prevC|."""
    return (
        2.0 * (df[HIGH] - df[LOW])
        - (df[CLOSE] - df[OPEN]).abs()
        + (df[OPEN] - df[CLOSE].shift(drift)).abs()
    )


@INDICATORS.register
class PriceDistance(Indicator):
    """Price Distance.

    What: a measure of total per-bar price travel that accounts for gaps.
    Best settings: drift 1.
    Edge cases: first bar has no prior close (NaN).
    Parity: pandas-ta ``pdist``.
    """

    spec = IndicatorSpec(
        name="pdist",
        category="volatility",
        aliases=("Price Distance",),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("pdist",),
        references=("pandas-ta pdist",),
        doc="ref/ta_docs/volatility/misc_volatility.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        drift: int = Field(default=1, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return pdist(df, self.params["drift"])
