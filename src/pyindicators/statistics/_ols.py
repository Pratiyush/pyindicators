"""Shared rolling ordinary-least-squares helper for the linear-regression family.

Fits ``y = intercept + slope * x`` over each trailing window with ``x = 0..length-1`` and
``y`` = the price window, via the closed-form normal equations (one rolling dot product).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def rolling_ols(series: pd.Series, length: int) -> tuple[pd.Series, pd.Series]:
    """Return (slope, intercept) Series of the rolling linear regression over ``length`` bars."""
    x = np.arange(length, dtype="float64")
    sum_x = x.sum()
    sum_x2 = float((x * x).sum())
    denom = length * sum_x2 - sum_x * sum_x  # > 0 for length >= 2
    sum_y = series.rolling(length, min_periods=length).sum()
    sum_xy = series.rolling(length, min_periods=length).apply(
        lambda y: float(np.dot(x, y)), raw=True
    )
    slope = (length * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / length
    return slope, intercept
