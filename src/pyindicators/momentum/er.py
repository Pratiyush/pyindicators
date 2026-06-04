"""ER — Kaufman's Efficiency Ratio: net change over total path length (0-1)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide


def er(close: pd.Series, length: int = 10) -> pd.Series:
    """Efficiency Ratio = |close - close_{t-N}| / sum(|close diff|, N), in [0, 1]."""
    change = close.diff(length).abs()
    volatility = close.diff().abs().rolling(length, min_periods=length).sum()
    return safe_divide(change, volatility)


@INDICATORS.register
class EfficiencyRatio(Indicator):
    """Efficiency Ratio.

    What: how directional recent movement is (1 = a straight line, 0 = pure chop).
    Best settings: ``length`` 10; drives KAMA's adaptive smoothing.
    Edge cases: flat window (zero path length) -> guarded to NaN.
    Parity: pandas-ta ``er``.
    """

    spec = IndicatorSpec(
        name="er",
        category="momentum",
        aliases=("Efficiency Ratio", "Kaufman Efficiency Ratio"),
        inputs=(CLOSE,),
        outputs=("er",),
        bounds={"er": (0.0, 1.0)},
        references=("Kaufman", "pandas-ta er"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=10, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return er(df[CLOSE], self.params["length"])
