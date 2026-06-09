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
from .features import build_features, build_output, parse_spec, rename_outputs
from .resample import align_to_base, resample_ohlcv
from .timeframe import Timeframe

__version__ = "0.3.0"

# Category packages — importing each registers its indicator classes. Imported AFTER the
# core symbols above (the statement between the import blocks keeps this order stable).
from . import (
    base,  # noqa: E402, F401
    candles,  # noqa: E402, F401
    cycle,  # noqa: E402, F401
    math_transform,  # noqa: E402, F401
    momentum,  # noqa: E402, F401
    price_transform,  # noqa: E402, F401
    relative,  # noqa: E402, F401
    statistics,  # noqa: E402, F401
    structure,  # noqa: E402, F401
    trend,  # noqa: E402, F401
    utils,  # noqa: E402, F401
    volatility,  # noqa: E402, F401
    volume,  # noqa: E402, F401
)

__all__ = [
    "INDICATORS",
    "Indicator",
    "IndicatorSpec",
    "Registry",
    "OHLCV_COLUMNS",
    "CATEGORIES",
    "Timeframe",
    "build_features",
    "build_output",
    "parse_spec",
    "rename_outputs",
    "align_to_base",
    "resample_ohlcv",
    "__version__",
]
