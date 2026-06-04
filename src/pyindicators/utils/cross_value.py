"""cross_value — 1 where a series crosses a constant threshold.

Composition/signal helper (e.g. RSI crossing 30/70), shipped as a plain function. Matches
``pandas_ta_classic.cross_value(series, value, above)``.
"""

from __future__ import annotations

import pandas as pd

from .crossover import crossover
from .crossunder import crossunder


def cross_value(series: pd.Series, value: float, above: bool = True) -> pd.Series:
    """1.0 where ``series`` crosses the constant ``value`` (above if ``above`` else below)."""
    level = pd.Series(float(value), index=series.index)
    return crossover(series, level) if above else crossunder(series, level)
