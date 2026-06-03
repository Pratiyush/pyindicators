"""Shared building blocks for the indicator library.

This module registers nothing (the plugin autoloader imports it harmlessly). It holds
the small set of numerically careful primitives every indicator reuses, plus the
``spec`` <-> ``(name, params)`` <-> parametrized-column helpers the rule/screener layer
will use. Everything here is **causal** (trailing-only) by construction.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from .base import Indicator


def require_columns(df: pd.DataFrame, cols: tuple[str, ...]) -> None:
    """Raise a clear error if any required OHLCV column is missing."""
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"indicator input is missing columns {missing}; have {list(df.columns)}")


def build_output(index: pd.Index, data: dict[str, Any]) -> pd.DataFrame:
    """Assemble an output frame aligned 1:1 to ``index`` with float64 columns.

    Centralizing this guarantees the contract: same index object as the input, column
    order == insertion order (== ``outputs``), dtype float64.
    """
    out = pd.DataFrame(index=index)
    for name, series in data.items():
        col = series if isinstance(series, pd.Series) else pd.Series(series, index=index)
        out[name] = col.astype("float64")
    return out


def wilder_rma(s: pd.Series, period: int) -> pd.Series:
    """Wilder's smoothing (a.k.a. RMA): EMA with ``alpha = 1/period``.

    Used by RSI/ATR/ADX. ``adjust=False`` gives the textbook recursive form (causal);
    ``min_periods=period`` produces the conventional NaN warm-up.
    """
    return s.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()


def ema(s: pd.Series, period: int) -> pd.Series:
    """Exponential MA, ``adjust=False`` (causal) with a clean ``period``-bar warm-up."""
    return s.ewm(span=period, adjust=False, min_periods=period).mean()


def true_range(df: pd.DataFrame) -> pd.Series:
    """Wilder's True Range: max(H-L, |H-prevC|, |L-prevC|). First bar is NaN (no prevC)."""
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [(high - low), (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    tr.iloc[:1] = np.nan  # no previous close for the first bar
    return tr


def typical_price(df: pd.DataFrame) -> pd.Series:
    """(high + low + close) / 3."""
    return (df["high"] + df["low"] + df["close"]) / 3.0


# --------------------------------------------------------------------------- #
# spec addressing: the rule/screener layer references indicators as either a
# ``{"name": ..., "params": {...}}`` dict (the research-frontmatter shape) or a
# compact ``"name:period=50,num_std=2"`` string.
# --------------------------------------------------------------------------- #

def _coerce(value: str) -> Any:
    for cast in (int, float):
        try:
            return cast(value)
        except ValueError:
            continue
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return value


def parse_spec(spec: str | dict) -> tuple[str, dict]:
    """Normalize an indicator spec into ``(name, params)``.

    Accepts the frontmatter dict ``{"name": "sma", "params": {"period": 50}}`` or the
    string ``"sma:period=50,foo=1.5"``.
    """
    if isinstance(spec, dict):
        return spec["name"], dict(spec.get("params") or {})
    name, _, rest = spec.partition(":")
    params: dict[str, Any] = {}
    for piece in filter(None, (p.strip() for p in rest.split(","))):
        key, _, val = piece.partition("=")
        params[key.strip()] = _coerce(val.strip())
    return name.strip(), params


def rename_outputs(frame: pd.DataFrame, indicator: Indicator) -> pd.DataFrame:
    """Rename an indicator's static output columns to collision-free, instance-specific
    names so multiple instances coexist on one frame (``sma_50``, ``sma_150``, ...).

    Uses ``indicator.primary_param``: when set and present in the instance params, every
    output column is suffixed with that param's value. Indicators with no primary param
    (``obv``, ``vwap``, ``macd``) keep their static names.
    """
    pp = indicator.primary_param
    if pp is None or pp not in indicator.params:
        return frame
    suffix = indicator.params[pp]
    return frame.rename(columns={c: f"{c}_{suffix}" for c in frame.columns})
