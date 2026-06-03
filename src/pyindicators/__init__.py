"""pyindicators — a modular, look-ahead-safe technical-analysis library.

One class per indicator, organised into category packages (``base``, ``trend``,
``momentum``, ``volatility``, ``volume``, ``statistics``, ``cycle``, ``price_transform``,
``candles``, ``math_transform``, ``utils``). Importing a category package registers its
indicators into :data:`INDICATORS`; this top-level module imports them so the registry is
populated on ``import pyindicators``.
"""

from __future__ import annotations

# Core contracts first (independent of the category packages).
from .core import (
    CATEGORIES,
    INDICATORS,
    OHLCV_COLUMNS,
    Indicator,
    IndicatorSpec,
    Registry,
)

__version__ = "0.2.0"

# Category packages — importing each registers its indicator classes. Imported AFTER the
# core symbols above (the statement between the import blocks keeps this order stable).
from . import base  # noqa: E402, F401

__all__ = [
    "INDICATORS",
    "Indicator",
    "IndicatorSpec",
    "Registry",
    "OHLCV_COLUMNS",
    "CATEGORIES",
    "__version__",
]
