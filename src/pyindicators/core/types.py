"""Canonical types and the OHLCV column contract shared across the library.

Every indicator reads from a pandas ``DataFrame`` whose columns are a subset of
:data:`OHLCV_COLUMNS` (lower-case ``open/high/low/close/volume``). Keeping the names in
one place means an indicator never hard-codes a column string.
"""

from __future__ import annotations

from typing import Literal

# Canonical OHLCV column names. Indicators declare which of these they read via
# ``IndicatorSpec.inputs``; the base class validates their presence before computing.
OPEN = "open"
HIGH = "high"
LOW = "low"
CLOSE = "close"
VOLUME = "volume"
OHLCV_COLUMNS: tuple[str, ...] = (OPEN, HIGH, LOW, CLOSE, VOLUME)

# The eleven category folders the library is organised into (mirrors ref/ta_docs).
Category = Literal[
    "base",
    "trend",
    "momentum",
    "volatility",
    "volume",
    "statistics",
    "cycle",
    "price_transform",
    "candles",
    "math_transform",
    "utils",
]

CATEGORIES: tuple[str, ...] = (
    "base",
    "trend",
    "momentum",
    "volatility",
    "volume",
    "statistics",
    "cycle",
    "price_transform",
    "candles",
    "math_transform",
    "utils",
)
