"""Fast Stochastic (%K / %D) — the un-smoothed stochastic (George Lane).

Where the close sits in the recent high-low range, scaled 0-100, with NO smoothing of %K
(that is what makes it "fast"); %D is a short SMA of the raw %K. The slow stochastic is this
with %K additionally smoothed. Composes ``base.sma``. See ``ref/ta_docs/momentum/Stochastic.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec, safe_divide


def stochf(df: pd.DataFrame, k: int = 14, d: int = 3) -> dict:
    """Fast Stochastic: raw %K and its SMA %D (both 0-100)."""
    ll = df[LOW].rolling(k, min_periods=k).min()
    hh = df[HIGH].rolling(k, min_periods=k).max()
    fast_k = safe_divide(100.0 * (df[CLOSE] - ll), hh - ll)  # NaN where HH == LL
    fast_d = sma(fast_k, d)
    return {"stochf_k": fast_k, "stochf_d": fast_d}


@INDICATORS.register
class FastStochastic(Indicator):
    """Fast Stochastic Oscillator (fast %K / %D).

    What: the raw (un-smoothed) position of close within the N-bar range (0-100); %D = SMA(%K).
    Best settings: 14/3 (or TA-Lib's 5/3); more responsive but noisier than the slow stochastic.
    Edge cases: HH == LL (flat window) -> %K undefined -> guarded to NaN.
    Parity: TA-Lib ``STOCHF`` (fastk/fastd, SMA matype) / pandas-ta ``stoch`` fast columns.
    """

    spec = IndicatorSpec(
        name="stochf",
        category="momentum",
        aliases=("Fast Stochastic", "STOCHF"),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("stochf_k", "stochf_d"),
        bounds={"stochf_k": (0.0, 100.0), "stochf_d": (0.0, 100.0)},
        talib_compatible=True,
        references=("Lane", "TA-Lib STOCHF", "pandas-ta stoch"),
        doc="ref/ta_docs/momentum/Stochastic.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        k: int = Field(default=14, ge=1)
        d: int = Field(default=3, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        return stochf(df, self.params["k"], self.params["d"])
