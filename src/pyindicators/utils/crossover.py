"""crossover — 1 where series ``a`` crosses ABOVE series ``b``.

A composition/signal helper (operates on two arbitrary series, e.g. fast vs slow MA), not a
single-symbol OHLCV indicator — so it ships as a plain function, not a registered ``Indicator``.
Matches ``pandas_ta_classic.cross(a, b, above=True)``.
"""

from __future__ import annotations

import pandas as pd


def crossover(a: pd.Series, b: pd.Series) -> pd.Series:
    """1.0 where ``a`` was below ``b`` and is now above it (``a<b`` prior, ``a>b`` now), else 0.0."""
    a = a.astype("float64")
    b = b.astype("float64")
    crossed = (a > b) & (a.shift(1) < b.shift(1))
    return crossed.astype("float64")
