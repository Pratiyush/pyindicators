"""utils/ — signal helpers.

Two kinds live here: single-series **indicators** (``lag``, ``decay``, ``edecay``,
``percent_rank``, ``roc1`` — registered, take a close series) and two-series **functions**
(``crossover``, ``crossunder``, ``crossany``, ``cross_value`` — composition operators that take
arbitrary derived series, so they are plain functions, not registered ``Indicator`` classes).
"""

from __future__ import annotations

from .cross_value import cross_value
from .crossany import crossany
from .crossover import crossover
from .crossunder import crossunder
from .decay import Decay, decay
from .edecay import ExponentialDecay, edecay
from .lag import Lag, lag
from .percent_rank import PercentRank, percent_rank
from .roc1 import ROC1, roc1

__all__ = [
    "crossover",
    "crossunder",
    "crossany",
    "cross_value",
    "Decay", "decay",
    "ExponentialDecay", "edecay",
    "Lag", "lag",
    "PercentRank", "percent_rank",
    "ROC1", "roc1",
]
