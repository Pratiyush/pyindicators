"""Disparity Index (Steve Nison / Pring) — percent deviation of price from its MA."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide


def disparity_index(close: pd.Series, length: int = 14) -> pd.Series:
    """Disparity Index = 100 * (close - SMA(close, length)) / SMA(close, length)."""
    m = sma(close, length)
    return 100.0 * safe_divide(close - m, m)


@INDICATORS.register
class DisparityIndex(Indicator):
    """Disparity Index.

    What: how far price sits above/below its moving average, in percent.
    Best settings: ``length`` 14; large |disparity| = overextended.
    Edge cases: zero MA guarded (prices are positive in practice); first length-1 bars NaN.
    Parity: standard disparity formula (validated against the explicit definition).
    """

    spec = IndicatorSpec(
        name="disparity_index",
        category="momentum",
        aliases=("Disparity Index",),
        inputs=(CLOSE,),
        outputs=("disparity_index",),
        references=("Pring", "Nison"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return disparity_index(df[CLOSE], self.params["length"])
