"""base/ — reusable core primitives.

Importing this package registers the base indicator classes and re-exports the pure
functions (``sma``, ``ema``, ``wma``, ``rma``, ``stdev``, ``variance``, ``true_range``)
that every downstream indicator composes from — never re-implement these inline.
"""

from __future__ import annotations

from .ema import EMA, ema
from .rma import RMA, rma
from .sma import SMA, sma
from .stdev import StdDev, stdev
from .true_range import TrueRange, true_range
from .variance import Variance, variance
from .wma import WMA, wma

__all__ = [
    # functions (for composition)
    "sma",
    "ema",
    "wma",
    "rma",
    "stdev",
    "variance",
    "true_range",
    # indicator classes
    "SMA",
    "EMA",
    "WMA",
    "RMA",
    "StdDev",
    "Variance",
    "TrueRange",
]
