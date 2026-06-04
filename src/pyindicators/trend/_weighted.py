"""Shared helper: a rolling moving average with an arbitrary fixed weight vector.

Used by the weight-vector MAs (FWMA, SINWMA, PWMA, ...). Weights are normalised to sum to 1
and dotted with each trailing window (oldest..newest order).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def weighted_ma(series: pd.Series, weights) -> pd.Series:
    """Rolling weighted average of ``series`` with the given ``weights`` (normalised)."""
    w = np.asarray(weights, dtype="float64")
    w = w / w.sum()
    n = w.size
    return series.rolling(n, min_periods=n).apply(lambda x: float(np.dot(x, w)), raw=True)
