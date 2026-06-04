"""crossany — 1 where series ``a`` crosses ``b`` in EITHER direction.

Composition/signal helper, shipped as a plain function. Composes :func:`crossover` and
:func:`crossunder` (= their logical OR).
"""

from __future__ import annotations

import pandas as pd

from .crossover import crossover
from .crossunder import crossunder


def crossany(a: pd.Series, b: pd.Series) -> pd.Series:
    """1.0 where ``a`` crosses above OR below ``b`` on this bar, else 0.0."""
    return ((crossover(a, b) > 0) | (crossunder(a, b) > 0)).astype("float64")
