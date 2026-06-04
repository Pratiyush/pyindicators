"""KDJ — the Chinese-charting stochastic variant (K, D, J).

A stochastic whose %K and %D are Wilder-smoothed (RMA) rather than SMA, plus a derived J line
(``J = 3K - 2D``) that overshoots 0-100 to flag extremes early. Composes ``base.rma``.
See ``ref/ta_docs/momentum/Stochastic.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import rma
from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec, safe_divide


def kdj(df: pd.DataFrame, length: int = 9, signal: int = 3) -> dict:
    """KDJ: RMA-smoothed %K, %D and the derived J line (J = 3K - 2D)."""
    ll = df[LOW].rolling(length, min_periods=length).min()
    hh = df[HIGH].rolling(length, min_periods=length).max()
    fast_k = safe_divide(100.0 * (df[CLOSE] - ll), hh - ll)  # NaN where HH == LL
    k = rma(fast_k, signal)
    d = rma(k, signal)
    j = 3.0 * k - 2.0 * d
    return {"kdj_k": k, "kdj_d": d, "kdj_j": j}


@INDICATORS.register
class KDJ(Indicator):
    """KDJ Indicator.

    What: a stochastic with RMA-smoothed K/D and a J line (3K-2D) that exaggerates turns.
    Best settings: length 9, signal 3; J < 0 or > 100 marks oversold/overbought extremes.
    Edge cases: HH == LL (flat window) -> %K undefined -> guarded to NaN; J is unbounded.
    Parity: pandas-ta ``kdj`` — converges on the tail (we use the canonical SMA-seeded Wilder
        RMA; pandas-ta restarts its ewm at the first valid bar through the warm-up).
    """

    spec = IndicatorSpec(
        name="kdj",
        category="momentum",
        aliases=("KDJ", "Random Index"),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("kdj_k", "kdj_d", "kdj_j"),
        bounds={"kdj_k": (0.0, 100.0), "kdj_d": (0.0, 100.0)},
        references=("pandas-ta kdj",),
        doc="ref/ta_docs/momentum/Stochastic.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=9, ge=1)
        signal: int = Field(default=3, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        return kdj(df, self.params["length"], self.params["signal"])
