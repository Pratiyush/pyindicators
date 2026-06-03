"""Feature assembly: the bridge from indicators to rules.

``build_features`` takes an OHLCV frame and a list of indicator specs (the
``Rule.requires`` shape — ``"sma:period=50"`` strings or ``{"name", "params"}`` dicts),
computes each indicator, renames its outputs to collision-free parametrized columns
(``sma_50``, ``bb_upper_20`` …), and joins them onto the frame. Rules then read those
columns through a ``BarContext``.
"""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from .common import parse_spec, rename_outputs
from .registry import INDICATORS

# Indicators whose constructor accepts an injected benchmark close series (the screener
# supplies it; standalone they degrade to a valid neutral series).
_BENCHMARK_AWARE = {"rs_line", "mansfield_rs"}


def _instantiate(name: str, params: dict, benchmark_close):
    if name in _BENCHMARK_AWARE and benchmark_close is not None:
        return INDICATORS.get(name)(benchmark_close=benchmark_close, **params)
    return INDICATORS.create(name, **params)


def build_features(
    df: pd.DataFrame,
    specs: Iterable[str | dict],
    *,
    benchmark_close: pd.Series | None = None,
) -> pd.DataFrame:
    """Return a copy of ``df`` with each spec's parametrized indicator columns joined on."""
    out = df.copy()
    for spec in specs:
        name, params = parse_spec(spec)
        ind = _instantiate(name, params, benchmark_close)
        computed = rename_outputs(ind.compute(df), ind)
        for col in computed.columns:
            out[col] = computed[col].to_numpy()
    return out
