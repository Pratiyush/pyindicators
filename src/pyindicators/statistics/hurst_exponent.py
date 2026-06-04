"""Hurst Exponent — rolling rescaled-range (R/S) estimate of trend persistence.

Per window: ``H = log(R/S) / log(n)`` where R is the range of the cumulative mean-deviations of
log returns and S is their standard deviation. H ~ 0.5 = random walk, > 0.5 = trending
(persistent), < 0.5 = mean-reverting. See ``ref/ta_docs/statistics/misc_statistics.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def _rescaled_range_h(window: np.ndarray) -> float:
    n = window.size
    deviations = np.cumsum(window - window.mean())
    spread = deviations.max() - deviations.min()
    s = window.std(ddof=0)
    if s == 0 or spread == 0:
        return np.nan
    return float(np.log(spread / s) / np.log(n))


def hurst_exponent(close: pd.Series, length: int = 100) -> pd.Series:
    """Rolling Hurst exponent (R/S) of log returns over ``length`` bars."""
    log_ret = np.log(close / close.shift(1))
    return log_ret.rolling(length, min_periods=length).apply(_rescaled_range_h, raw=True)


@INDICATORS.register
class HurstExponent(Indicator):
    """Hurst Exponent.

    What: a regime gauge — ~0.5 random walk, > 0.5 trending/persistent, < 0.5 mean-reverting.
    Best settings: ``length`` 100 (needs a long window for a stable R/S estimate).
    Edge cases: a flat window (zero stdev/range) -> NaN; first bar's log return is NaN.
    Parity: rolling rescaled-range estimate (validated structurally: a random walk -> ~0.5).
    """

    spec = IndicatorSpec(
        name="hurst_exponent",
        category="statistics",
        aliases=("Hurst Exponent", "Rescaled Range"),
        inputs=(CLOSE,),
        outputs=("hurst_exponent",),
        references=("Hurst", "Chan (regime)"),
        doc="ref/ta_docs/statistics/misc_statistics.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=100, ge=8)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return hurst_exponent(df[CLOSE], self.params["length"])
