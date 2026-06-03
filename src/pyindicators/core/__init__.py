"""Core contracts: the Indicator base, its typed spec, the registry, and shared policy."""

from __future__ import annotations

from .edgecases import clamp, require_columns, safe_divide
from .indicator import Indicator
from .metadata import IndicatorSpec
from .registry import INDICATORS, Registry
from .types import (
    CATEGORIES,
    CLOSE,
    HIGH,
    LOW,
    OHLCV_COLUMNS,
    OPEN,
    VOLUME,
    Category,
)

__all__ = [
    "Indicator",
    "IndicatorSpec",
    "INDICATORS",
    "Registry",
    "require_columns",
    "safe_divide",
    "clamp",
    "OHLCV_COLUMNS",
    "OPEN",
    "HIGH",
    "LOW",
    "CLOSE",
    "VOLUME",
    "CATEGORIES",
    "Category",
]
