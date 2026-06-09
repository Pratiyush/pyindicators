"""Mansfield Relative Strength (Weinstein) — the RS line normalized by its own MA.

``(rp / SMA(rp, length) - 1) * 100`` where ``rp = close / benchmark``. Zero-line crossings
flag relative-trend turns. Benchmark-aware via the injected ``benchmark`` column (see
``rs_line``); with no benchmark it degrades to a flat 0.0 line after warm-up.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from .rs_line import benchmark_close


@INDICATORS.register
class MansfieldRS(Indicator):
    """Mansfield RS.

    What: the price-relative line normalized by its own moving average,
    ``(RP / SMA(RP, length) - 1) * 100``.
    Best settings: length 52 (weekly Weinstein stage analysis); > 0 = relative uptrend.
    Edge cases: needs a ``benchmark`` column (else a flat 0.0 line after warm-up). Causal.
    """

    spec = IndicatorSpec(
        name="mansfield_rs",
        category="relative",
        aliases=("Mansfield Relative Strength", "MRS"),
        inputs=(CLOSE,),
        outputs=("mansfield_rs",),
        references=("Weinstein — Secrets for Profiting in Bull and Bear Markets",),
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=52, ge=2)
        benchmark: str = Field(default="SPY")

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        length = self.params["length"]
        rp = df[CLOSE] / benchmark_close(df)
        ma = rp.rolling(length, min_periods=length).mean()
        return (rp / ma - 1.0) * 100.0
