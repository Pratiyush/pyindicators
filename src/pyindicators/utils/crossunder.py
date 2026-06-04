"""crossunder — 1 where series ``a`` crosses BELOW series ``b``.

Composition/signal helper (two arbitrary series), shipped as a plain function, not a registered
``Indicator``. Matches ``pandas_ta_classic.cross(a, b, above=False)``.
"""

from __future__ import annotations

import pandas as pd


def crossunder(a: pd.Series, b: pd.Series) -> pd.Series:
    """1.0 where ``a`` was above ``b`` and is now below it (``a>b`` prior, ``a<b`` now), else 0.0."""
    a = a.astype("float64")
    b = b.astype("float64")
    crossed = (a < b) & (a.shift(1) > b.shift(1))
    return crossed.astype("float64")
