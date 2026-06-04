"""Mass Index (Dorsey) — reversal detector via range expansion.

``MASSI = sum( EMA(H-L, fast) / EMA(EMA(H-L, fast), fast), slow )``. A "reversal bulge"
(rising above 27 then falling below 26.5) flags a coming reversal. Composes ``base.ema``.
See ``ref/ta_docs/volatility/misc_volatility.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec, safe_divide


def massi(df: pd.DataFrame, fast: int = 9, slow: int = 25) -> pd.Series:
    """Mass Index: rolling sum of the single/double EMA ratio of the high-low range."""
    hl_range = df[HIGH] - df[LOW]
    ema1 = ema(hl_range, fast)
    ema2 = ema(ema1, fast)
    ratio = safe_divide(ema1, ema2)
    return ratio.rolling(slow, min_periods=slow).sum()


@INDICATORS.register
class MassIndex(Indicator):
    """Mass Index.

    What: detects reversals from high-low range expansion (the "reversal bulge").
    Best settings: fast 9, slow 25; bulge > 27 then < 26.5.
    Edge cases: flat range -> EMA ratio 1; long warm-up (double EMA + slow sum).
    Parity: pandas-ta ``massi``.
    """

    spec = IndicatorSpec(
        name="massi",
        category="volatility",
        aliases=("Mass Index",),
        inputs=(HIGH, LOW),
        outputs=("massi",),
        references=("Dorsey", "pandas-ta massi"),
        doc="ref/ta_docs/volatility/misc_volatility.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        fast: int = Field(default=9, ge=1)
        slow: int = Field(default=25, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return massi(df, self.params["fast"], self.params["slow"])
