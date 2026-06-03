"""pyindicators — a modular, look-ahead-safe technical-indicator library (pandas/numpy).

Importing the package registers every built-in indicator into ``INDICATORS``::

    import pyindicators as pyi
    rsi = pyi.INDICATORS.create("rsi", period=14)
    out = rsi.compute(df)            # df: canonical OHLCV frame
    feats = pyi.build_features(df, ["sma:period=50", "rsi:period=14"])
"""

from __future__ import annotations

# Importing the family modules runs their @INDICATORS.register decorators.
from . import (  # noqa: E402,F401  (import-for-side-effects, after core symbols)
    adaptive,
    custom,
    flow,
    momentum,
    relative,
    structure,
    trend,
    volatility,
    volume,
)
from .base import Indicator
from .common import (
    build_output,
    ema,
    parse_spec,
    rename_outputs,
    require_columns,
    true_range,
    typical_price,
    wilder_rma,
)
from .compute import build_features
from .registry import INDICATORS, Registry
from .resample import align_to_base, resample_ohlcv
from .types import OHLCV_COLUMNS, Timeframe

__version__ = "0.1.0"

__all__ = [
    "Indicator",
    "Registry",
    "INDICATORS",
    "Timeframe",
    "OHLCV_COLUMNS",
    "build_features",
    "build_output",
    "ema",
    "wilder_rma",
    "true_range",
    "typical_price",
    "require_columns",
    "parse_spec",
    "rename_outputs",
    "resample_ohlcv",
    "align_to_base",
    "__version__",
]
