"""Feature assembly — compose indicators into a parametrized feature frame.

The composition layer that turns an OHLCV frame plus a list of indicator *specs* into a
single frame of collision-free, parametrized columns (``sma_50``, ``rolling_high_252`` ...)
that rules and screeners read. Pure and causal: it only renames and joins the indicators'
own (already look-ahead-safe) outputs, never recomputes time.

Small, independently testable pieces:
- ``parse_spec``     -- spec string/dict -> ``(name, params)``
- ``build_output``   -- assemble a float64 frame on an index
- ``primary_param``  -- the param whose value disambiguates an indicator's columns
- ``rename_outputs`` -- static output names -> parametrized (``sma`` -> ``sma_50``)
- ``build_features`` -- the public entry point
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import numpy as np
import pandas as pd

from .core import INDICATORS, Indicator

#: Param names that are conventions/flags, never the column-naming disambiguator.
_FLAG_PARAMS = frozenset({"talib_compatible", "ddof"})

#: A spec selects one registered indicator + its params.
Spec = str | dict


def _coerce(value: str) -> Any:
    """Lexically coerce a spec-string value: int -> float -> bool -> str."""
    for cast in (int, float):
        try:
            return cast(value)
        except ValueError:
            continue
    low = value.lower()
    if low in {"true", "false"}:
        return low == "true"
    return value


def parse_spec(spec: Spec) -> tuple[str, dict]:
    """Normalize an indicator spec into ``(name, params)``.

    Accepts the dict form ``{"name": "sma", "params": {"length": 50}}`` or the compact
    string ``"sma:length=50,mult=2.0"`` (comma-separated ``key=value``; each value coerced
    int -> float -> bool -> str). The indicator's pydantic ``Params`` is the authoritative
    validator downstream.
    """
    if isinstance(spec, dict):
        return spec["name"], dict(spec.get("params") or {})
    name, _, rest = spec.partition(":")
    params: dict[str, Any] = {}
    for piece in filter(None, (p.strip() for p in rest.split(","))):
        key, _, val = piece.partition("=")
        params[key.strip()] = _coerce(val.strip())
    return name.strip(), params


def build_output(index: pd.Index, data: dict[str, Any]) -> pd.DataFrame:
    """Assemble a float64 frame on ``index``; column order == insertion order."""
    out = pd.DataFrame(index=index)
    for name, series in data.items():
        col = series if isinstance(series, pd.Series) else pd.Series(series, index=index)
        out[name] = col.astype("float64")
    return out


def primary_param(indicator: Indicator) -> str | None:
    """The param whose value disambiguates an indicator's output columns.

    Inference: the first ``Params`` field (definition order) whose value is a real number
    (``int``/``float``, not ``bool``) and is not a naming-irrelevant flag. Indicators with
    no such param (param-less, or TA-standard multi-line series like ``macd``) return
    ``None`` and keep their static output names.
    """
    for key, val in indicator.params.items():
        if key in _FLAG_PARAMS or isinstance(val, bool):
            continue
        if isinstance(val, (int, float)):
            return key
    return None


def rename_outputs(frame: pd.DataFrame, indicator: Indicator) -> pd.DataFrame:
    """Suffix every output column with the primary param's value (``sma`` -> ``sma_50``).

    No primary param -> the frame is returned unchanged (static names, e.g. ``obv``/``macd``).
    """
    pp = primary_param(indicator)
    if pp is None:
        return frame
    suffix = indicator.params[pp]
    return frame.rename(columns={c: f"{c}_{suffix}" for c in frame.columns})


def build_features(
    df: pd.DataFrame,
    specs: Iterable[Spec],
    *,
    benchmark_close: pd.Series | None = None,
) -> pd.DataFrame:
    """Return a copy of ``df`` with each spec's parametrized indicator columns joined on.

    Causality is inherited from the indicators (each is truncation-invariant); this only
    renames + joins. Identical specs are computed once. Raises ``ValueError`` if two
    distinct specs resolve to the same feature column (a genuine collision).

    ``benchmark_close`` (a series aligned 1:1 to ``df``) is injected as a ``benchmark``
    column for benchmark-aware indicators (``rs_line``, ``mansfield_rs``); others ignore it.
    """
    if benchmark_close is None:
        work = df
    else:
        bench = np.asarray(benchmark_close, dtype="float64")
        if len(bench) != len(df):
            raise ValueError(f"benchmark_close length {len(bench)} != frame length {len(df)}")
        work = df.assign(benchmark=bench)

    out = df.copy()
    seen: set[str] = set()
    produced: set[str] = set()
    for spec in specs:
        name, params = parse_spec(spec)
        key = f"{name}:{sorted(params.items())}"
        if key in seen:
            continue
        seen.add(key)
        ind = INDICATORS.create(name, **params)
        computed = rename_outputs(ind.compute(work), ind)
        for col in computed.columns:
            if col in produced:
                raise ValueError(f"feature column collision: {col!r}")
            produced.add(col)
            out[col] = computed[col].to_numpy()
    return out
