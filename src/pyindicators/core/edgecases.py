"""The universal edge-case policy, centralised so every indicator stays small.

CONVENTIONS.md mandates one consistent treatment of the recurring numeric hazards:
division by zero, flat/constant windows, and warm-up. Indicators call these helpers
instead of re-implementing guards (and getting them subtly different).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def require_columns(df: pd.DataFrame, cols: tuple[str, ...]) -> None:
    """Raise a clear error if any required column is missing from ``df``."""
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"input frame missing columns {missing}; have {list(df.columns)}")


def safe_divide(
    num: pd.Series | float | int,
    den: pd.Series,
    fill: float = np.nan,
) -> pd.Series:
    """Element-wise ``num / den`` returning ``fill`` wherever ``den == 0``.

    Guards the single most common indicator bug (flat series make ranges, summed
    gains/losses, and variances zero). NaNs already present (warm-up) propagate as NaN.
    """
    num_s = num if isinstance(num, pd.Series) else pd.Series(num, index=den.index)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = num_s / den
    return out.mask(den == 0, fill)


def clamp(s: pd.Series, lo: float, hi: float) -> pd.Series:
    """Clip ``s`` into the open-ish interval ``[lo, hi]`` (e.g. Fisher needs strictly < |1|)."""
    return s.clip(lower=lo, upper=hi)
