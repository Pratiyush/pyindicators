"""Indicator contract.

An Indicator is an individual, standalone, reusable unit — one math primitive over
an OHLCV frame. Indicators know nothing about rules or strategies and are shared
across all of them. Concrete indicators land in Phase 2 (trend/momentum/...).
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from typing import ClassVar

import pandas as pd
from pydantic import BaseModel


class Indicator(ABC):
    name: ClassVar[str]
    params_model: ClassVar[type[BaseModel] | None] = None
    outputs: ClassVar[tuple[str, ...]] = ()

    # --- optional metadata (all defaulted; existing indicators need not set them) ---
    #: The single param whose value disambiguates output column names when an
    #: indicator is instantiated multiple times (e.g. ``"period"`` -> ``sma_50``).
    #: ``None`` means the static ``outputs`` names are kept as-is (e.g. ``obv``, ``macd``).
    primary_param: ClassVar[str | None] = None
    #: Output column -> ``(low, high)`` inclusive bounds, used by the generic bounds
    #: property test (e.g. RSI -> ``{"rsi": (0.0, 100.0)}``). Empty means unbounded.
    bounds: ClassVar[dict[str, tuple[float, float]]] = {}
    #: Whether the indicator is causal (value at bar ``i`` depends only on rows ``<= i``).
    #: The look-ahead meta-test runs over every indicator with ``causal = True``.
    causal: ClassVar[bool] = True
    #: Bumped when a formula changes so the (future) on-disk cache invalidates.
    version: ClassVar[int] = 1

    def __init__(self, **params):
        self.params = (
            self.params_model(**params).model_dump() if self.params_model else dict(params)
        )

    @abstractmethod
    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return a frame indexed like ``df`` with columns == ``self.outputs``."""

    def cache_key(self) -> str:
        payload = json.dumps(
            {"name": self.name, "version": self.version, "params": self.params},
            sort_keys=True,
            default=str,
        )
        return f"{self.name}-{hashlib.sha1(payload.encode()).hexdigest()[:12]}"
