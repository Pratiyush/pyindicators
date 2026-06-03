"""Vortex Indicator (VI+ / VI-) — trend start detection (Botes & Siepman 2010).

``VI+ = sum(|High_t - Low_{t-1}|, N) / sum(TR, N)``; ``VI- = sum(|Low_t - High_{t-1}|, N)
/ sum(TR, N)``. Crossovers flag new trends. Composes ``base.true_range``.
See ``ref/ta_docs/trend/Vortex.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import true_range
from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec, safe_divide


def vortex(df: pd.DataFrame, length: int = 14) -> dict:
    """Vortex VI+ and VI- over ``length`` bars."""
    vm_plus = (df[HIGH] - df[LOW].shift(1)).abs()
    vm_minus = (df[LOW] - df[HIGH].shift(1)).abs()
    tr_sum = true_range(df).rolling(length, min_periods=length).sum()
    vi_plus = safe_divide(vm_plus.rolling(length, min_periods=length).sum(), tr_sum)
    vi_minus = safe_divide(vm_minus.rolling(length, min_periods=length).sum(), tr_sum)
    return {"vi_plus": vi_plus, "vi_minus": vi_minus}


@INDICATORS.register
class Vortex(Indicator):
    """Vortex Indicator.

    What: two lines (VI+/VI-) capturing positive/negative trend movement; crossovers = new trend.
    Best settings: ``length`` 14 (21-34 smoother).
    Edge cases: sum(TR) == 0 (flat, no gaps) -> guarded to NaN.
    Parity: pandas-ta ``vortex`` (VTXP/VTXM). Not in core TA-Lib.
    """

    spec = IndicatorSpec(
        name="vortex",
        category="trend",
        aliases=("Vortex Indicator", "VI"),
        inputs=(HIGH, LOW, "close"),
        outputs=("vi_plus", "vi_minus"),
        references=("Botes & Siepman 2010", "pandas-ta vortex"),
        doc="ref/ta_docs/trend/Vortex.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        return vortex(df, self.params["length"])
