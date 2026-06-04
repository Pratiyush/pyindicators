"""BRAR — Sentiment/Energy indicators AR and BR (a Chinese-market pair).

AR ("popularity") gauges intraday energy from the open: ``100 * sum(high-open) / sum(open-low)``.
BR ("buy/sell willingness") gauges energy from the prior close: ``100 * sum(max(high-prevC,0)) /
sum(max(prevC-low,0))``. Both over ``length`` bars. Composes rolling sums. See
``ref/ta_docs/momentum/misc_momentum.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import (
    CLOSE,
    HIGH,
    INDICATORS,
    LOW,
    OPEN,
    Indicator,
    IndicatorSpec,
    safe_divide,
)


def brar(df: pd.DataFrame, length: int = 26, scalar: float = 100.0) -> dict:
    """AR and BR energy ratios over ``length`` bars."""
    o, h, low_, c = df[OPEN], df[HIGH], df[LOW], df[CLOSE]
    prev_c = c.shift(1)
    ho = (h - o).rolling(length, min_periods=length).sum()
    ol = (o - low_).rolling(length, min_periods=length).sum()
    hcy = (h - prev_c).clip(lower=0).rolling(length, min_periods=length).sum()
    cyl = (prev_c - low_).clip(lower=0).rolling(length, min_periods=length).sum()
    return {
        "ar": scalar * safe_divide(ho, ol),
        "br": scalar * safe_divide(hcy, cyl),
    }


@INDICATORS.register
class BRAR(Indicator):
    """BRAR (AR & BR).

    What: two energy/sentiment oscillators — AR from the open, BR from the prior close.
    Best settings: ``length`` 26; ~100 = balance, >> 100 = strong/overbought, << 100 = weak.
    Edge cases: zero down-energy denominator -> guarded to NaN; BR needs a prior close (warm-up).
    Parity: pandas-ta ``brar`` (AR/BR).
    """

    spec = IndicatorSpec(
        name="brar",
        category="momentum",
        aliases=("BRAR", "AR/BR", "Sentiment"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("ar", "br"),
        references=("pandas-ta brar",),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=26, ge=1)
        scalar: float = Field(default=100.0, gt=0.0)

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return brar(df, p["length"], p["scalar"])
