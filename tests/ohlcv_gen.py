"""Shared OHLCV generators for indicator tests.

`valid_ohlcv_frames` is the reusable hypothesis strategy that emits canonical OHLCV
frames satisfying the data-quality invariants *by construction* (no draw-and-filter).
`deterministic_frame` is a fixed, reproducible long frame for golden/bounds tests.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from hypothesis import strategies as st

from pyindicators import OHLCV_COLUMNS

_START = pd.Timestamp("2000-01-03", tz="UTC")  # a Monday


def _assemble(closes, open_off, up_off, down_off, vols) -> pd.DataFrame:
    n = len(closes)
    c = np.asarray(closes, dtype="float64")
    o = c * (1.0 + np.asarray(open_off, dtype="float64"))
    hi = np.maximum(o, c) * (1.0 + np.abs(np.asarray(up_off, dtype="float64")))
    lo = np.minimum(o, c) * (1.0 - np.abs(np.asarray(down_off, dtype="float64")))
    ts = pd.date_range(_START, periods=n, freq="D", tz="UTC")
    df = pd.DataFrame(
        {
            "ts": ts,
            "open": o,
            "high": hi,
            "low": lo,
            "close": c,
            "close_raw": c,
            "volume": np.asarray(vols, dtype="float64"),
            "adj_factor": 1.0,
        }
    )
    return df[OHLCV_COLUMNS]


@st.composite
def valid_ohlcv_frames(draw, min_rows: int = 1, max_rows: int = 120) -> pd.DataFrame:
    n = draw(st.integers(min_value=min_rows, max_value=max_rows))
    flt = lambda lo, hi: st.floats(  # noqa: E731
        min_value=lo, max_value=hi, allow_nan=False, allow_infinity=False
    )
    closes = draw(st.lists(flt(1.0, 1e5), min_size=n, max_size=n))
    open_off = draw(st.lists(flt(-0.05, 0.05), min_size=n, max_size=n))
    up_off = draw(st.lists(flt(0.0, 0.05), min_size=n, max_size=n))
    down_off = draw(st.lists(flt(0.0, 0.05), min_size=n, max_size=n))
    vols = draw(st.lists(st.integers(min_value=0, max_value=10**9), min_size=n, max_size=n))
    return _assemble(closes, open_off, up_off, down_off, vols)


def deterministic_frame(n: int = 400, seed: int = 7) -> pd.DataFrame:
    """A fixed random-walk frame long enough to clear 252-bar warm-ups."""
    rng = np.random.default_rng(seed)
    closes = np.maximum(100.0 + np.cumsum(rng.normal(0, 1, n)), 1.0)
    open_off = rng.normal(0, 0.005, n)
    up_off = np.abs(rng.normal(0, 0.005, n))
    down_off = np.abs(rng.normal(0, 0.005, n))
    vols = rng.integers(10**5, 10**6, n)
    return _assemble(closes, open_off, up_off, down_off, vols)
