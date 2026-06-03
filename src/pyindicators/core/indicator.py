"""The abstract :class:`Indicator` base class — the uniform contract for every indicator.

Subclasses provide a :class:`IndicatorSpec` (``spec``), an optional nested pydantic
``Params`` model, and implement :meth:`_compute` (the raw math). The base class handles
everything repetitive and safety-critical:

- validates that the input frame carries the OHLCV columns the spec declares,
- validates/normalises parameters through the ``Params`` model,
- coerces the result to the exact output contract: a float64 ``DataFrame`` indexed like the
  input, with columns equal to ``spec.outputs`` in order,
- exposes a stable ``cache_key`` derived from name + params.

Causality (no look-ahead) and warm-up NaNs are the indicator's responsibility (use trailing
windows / ``min_periods``); the registry-driven meta-tests verify them for every indicator.
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from typing import ClassVar

import pandas as pd
from pydantic import BaseModel

from .metadata import IndicatorSpec


class Indicator(ABC):
    """Base class for all indicators. See module docstring for the contract."""

    #: Declarative metadata — every concrete indicator MUST set this.
    spec: ClassVar[IndicatorSpec]
    #: Optional nested pydantic model describing parameters; ``None`` means no parameters.
    Params: ClassVar[type[BaseModel] | None] = None

    def __init__(self, **params: object) -> None:
        if self.Params is not None:
            self.params: dict[str, object] = self.Params(**params).model_dump()
        elif params:
            raise TypeError(f"{self.name} takes no parameters, got {sorted(params)}")
        else:
            self.params = {}

    # --- convenience proxies onto the spec -------------------------------------------
    @property
    def name(self) -> str:
        return self.spec.name

    @property
    def outputs(self) -> tuple[str, ...]:
        return self.spec.outputs

    # --- the public entry point --------------------------------------------------------
    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate inputs, run :meth:`_compute`, and enforce the output contract."""
        self._require_inputs(df)
        raw = self._compute(df)
        return self._finalize(df.index, raw)

    @abstractmethod
    def _compute(self, df: pd.DataFrame) -> pd.DataFrame | pd.Series | dict[str, pd.Series]:
        """Return the raw result as a Series (single output), or dict/DataFrame keyed by
        output name. The base class coerces it to the canonical output frame."""

    # --- internals ---------------------------------------------------------------------
    def _require_inputs(self, df: pd.DataFrame) -> None:
        missing = [c for c in self.spec.inputs if c not in df.columns]
        if missing:
            raise ValueError(
                f"{self.name}: input frame missing columns {missing}; have {list(df.columns)}"
            )

    def _finalize(
        self,
        index: pd.Index,
        raw: pd.DataFrame | pd.Series | dict[str, pd.Series],
    ) -> pd.DataFrame:
        if isinstance(raw, pd.DataFrame):
            data: dict[str, object] = {c: raw[c] for c in raw.columns}
        elif isinstance(raw, pd.Series):
            data = {self.spec.outputs[0]: raw}
        elif isinstance(raw, dict):
            data = raw
        else:  # pragma: no cover - defensive; a subclass returning the wrong type is a bug
            raise TypeError(f"{self.name}._compute returned unsupported type {type(raw)!r}")

        out = pd.DataFrame(index=index)
        for col in self.spec.outputs:
            if col not in data:
                raise ValueError(f"{self.name}: _compute did not produce output '{col}'")
            series = data[col]
            if not isinstance(series, pd.Series):
                series = pd.Series(series, index=index)
            out[col] = series.astype("float64")
        return out

    def cache_key(self) -> str:
        payload = json.dumps(
            {"name": self.name, "version": 1, "params": self.params},
            sort_keys=True,
            default=str,
        )
        return f"{self.name}-{hashlib.sha1(payload.encode()).hexdigest()[:12]}"
