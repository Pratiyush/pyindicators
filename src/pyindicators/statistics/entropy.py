"""Rolling Shannon Entropy — distributional uncertainty of price over a window (statistics).

``p = close / sum(close, N)``; ``entropy = sum(-p * log_base(p), N)``. See
``ref/ta_docs/statistics/misc_statistics.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def entropy(close: pd.Series, length: int = 10, base: float = 2.0) -> pd.Series:
    """Rolling Shannon entropy of ``close`` over ``length`` bars (log base ``base``).

    Each window's probabilities share that window's sum as the denominator (proper per-window
    Shannon entropy), so a constant series yields ``log_base(length)``.
    """
    log_base = np.log(base)

    def _window_entropy(window: np.ndarray) -> float:
        p = window / window.sum()
        return float(-(p * np.log(p)).sum() / log_base)

    return close.rolling(length, min_periods=length).apply(_window_entropy, raw=True)


@INDICATORS.register
class Entropy(Indicator):
    """Rolling Shannon Entropy.

    What: distributional uncertainty of price over ``length`` bars (higher = more uniform).
    Best settings: ``length`` 10, base 2.
    Edge cases: prices are positive (>0), so log is well-defined; first bars NaN.
    Parity: pandas-ta ``entropy``.
    """

    spec = IndicatorSpec(
        name="entropy",
        category="statistics",
        aliases=("Shannon Entropy",),
        inputs=(CLOSE,),
        outputs=("entropy",),
        references=("pandas-ta entropy",),
        doc="ref/ta_docs/statistics/misc_statistics.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=10, ge=1)
        base: float = Field(default=2.0, gt=1.0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return entropy(df[CLOSE], self.params["length"], self.params["base"])
