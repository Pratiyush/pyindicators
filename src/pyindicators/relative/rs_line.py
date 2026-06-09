"""RS Line (price relative) — ``close / benchmark`` (rising == outperforming).

Benchmark-aware: the benchmark close is supplied out-of-band as a ``benchmark`` column
(``build_features(..., benchmark_close=...)`` injects it). With no benchmark column it
degrades to a valid, causal series (ratio == 1.0), so the registry-driven meta-tests pass
on a plain OHLCV frame with no special-casing.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def benchmark_close(df: pd.DataFrame) -> pd.Series:
    """The benchmark close: the injected ``benchmark`` column, else ``close`` (ratio == 1)."""
    return df["benchmark"] if "benchmark" in df.columns else df[CLOSE]


@INDICATORS.register
class RSLine(Indicator):
    """RS Line.

    What: the price-relative line ``close / benchmark`` (Mansfield/IBD). Rising = the symbol
    is outperforming its benchmark; falling = lagging.
    Edge cases: needs a ``benchmark`` column (``build_features`` injects it); without one it
    is a flat 1.0 line. Causal (point-wise ratio).
    """

    spec = IndicatorSpec(
        name="rs_line",
        category="relative",
        aliases=("Price Relative", "RS Line"),
        inputs=(CLOSE,),
        outputs=("rs_line",),
        references=("Mansfield", "IBD RS line"),
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        benchmark: str = Field(default="SPY")  # informational label only

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return df[CLOSE] / benchmark_close(df)
