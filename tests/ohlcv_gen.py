"""Shared OHLCV generators for indicator tests.

``valid_ohlcv_frames`` is a hypothesis strategy emitting frames that satisfy the OHLCV
invariants by construction (high >= max(o,c,l), low <= min(o,c,h), volume >= 0).
``deterministic_frame`` is a fixed 400-bar random walk for golden/bounds/parity tests.
``real_frame`` loads a committed fixture of *genuine* market data (real gaps, real volume) so
parity is cross-checked against actual price action, not only synthetic series.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from hypothesis import strategies as st

from pyindicators import OHLCV_COLUMNS

_DATA_DIR = Path(__file__).parent / "data"


def _assemble(closes, open_off, up_off, down_off, vols) -> pd.DataFrame:
    c = np.asarray(closes, dtype="float64")
    o = c * (1.0 + np.asarray(open_off, dtype="float64"))
    hi = np.maximum(o, c) * (1.0 + np.abs(np.asarray(up_off, dtype="float64")))
    lo = np.minimum(o, c) * (1.0 - np.abs(np.asarray(down_off, dtype="float64")))
    df = pd.DataFrame(
        {
            "open": o,
            "high": hi,
            "low": lo,
            "close": c,
            "volume": np.asarray(vols, dtype="float64"),
        }
    )
    return df[list(OHLCV_COLUMNS)]


@st.composite
def valid_ohlcv_frames(draw, min_rows: int = 1, max_rows: int = 120) -> pd.DataFrame:
    n = draw(st.integers(min_value=min_rows, max_value=max_rows))

    def flt(lo, hi):
        return st.floats(min_value=lo, max_value=hi, allow_nan=False, allow_infinity=False)

    closes = draw(st.lists(flt(1.0, 1e5), min_size=n, max_size=n))
    open_off = draw(st.lists(flt(-0.05, 0.05), min_size=n, max_size=n))
    up_off = draw(st.lists(flt(0.0, 0.05), min_size=n, max_size=n))
    down_off = draw(st.lists(flt(0.0, 0.05), min_size=n, max_size=n))
    vols = draw(st.lists(st.integers(min_value=0, max_value=10**9), min_size=n, max_size=n))
    return _assemble(closes, open_off, up_off, down_off, vols)


def frame(close, *, high=None, low=None, open_=None, volume=None) -> pd.DataFrame:
    """Build a small OHLCV frame from an explicit close (and optional H/L/O/V) for golden
    tests. Unspecified H/L/O default to ``close``; volume defaults to ones."""
    close = np.asarray(close, dtype="float64")
    n = len(close)
    high = close if high is None else np.asarray(high, dtype="float64")
    low = close if low is None else np.asarray(low, dtype="float64")
    open_ = close if open_ is None else np.asarray(open_, dtype="float64")
    volume = np.ones(n) if volume is None else np.asarray(volume, dtype="float64")
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume}
    )


def deterministic_frame(n: int = 400, seed: int = 7) -> pd.DataFrame:
    """A fixed random-walk frame long enough to clear long warm-ups (ADX/T3/etc.)."""
    rng = np.random.default_rng(seed)
    closes = np.maximum(100.0 + np.cumsum(rng.normal(0, 1, n)), 1.0)
    open_off = rng.normal(0, 0.005, n)
    up_off = np.abs(rng.normal(0, 0.005, n))
    down_off = np.abs(rng.normal(0, 0.005, n))
    vols = rng.integers(10**5, 10**6, n)
    return _assemble(closes, open_off, up_off, down_off, vols)


def real_frame(symbol: str = "aapl") -> pd.DataFrame:
    """Genuine daily OHLCV from a committed fixture (real gaps/volatility/volume).

    Used by the real-data parity sweep so indicators are validated against actual market
    behaviour, not just synthetic walks. ``tests/data/<symbol>_daily.csv``.
    """
    df = pd.read_csv(_DATA_DIR / f"{symbol}_daily.csv")
    return df[list(OHLCV_COLUMNS)].reset_index(drop=True)
