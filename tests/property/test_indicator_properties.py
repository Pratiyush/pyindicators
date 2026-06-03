"""Property tests that need post-warm-up values: bounds, warm-up NaN, and a self-check
that the OHLCV generator only emits valid frames.
"""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given

from ohlcv_gen import deterministic_frame, valid_ohlcv_frames
from pyindicators import INDICATORS

NAMES = INDICATORS.names()
LONG = deterministic_frame()


@given(df=valid_ohlcv_frames(min_rows=1, max_rows=80))
def test_generator_emits_valid_ohlcv(df):
    # The generator must satisfy the same invariants the data-quality suite enforces.
    assert (df["high"] >= df[["open", "close", "low"]].max(axis=1)).all()
    assert (df["low"] <= df[["open", "close", "high"]].min(axis=1)).all()
    assert (df["high"] >= df["low"]).all()
    assert (df["volume"] >= 0).all()
    assert df["ts"].is_monotonic_increasing and df["ts"].is_unique
    assert str(df["ts"].dt.tz) == "UTC"


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
def test_declared_bounds_respected(name):
    ind = INDICATORS.create(name)
    if not ind.bounds:
        pytest.skip(f"{name} declares no bounds")
    out = ind.compute(LONG)
    for col, (lo, hi) in ind.bounds.items():
        vals = out[col].to_numpy()
        finite = vals[np.isfinite(vals)]
        assert (finite >= lo - 1e-9).all(), f"{name}.{col} < {lo}: min {finite.min()}"
        assert (finite <= hi + 1e-9).all(), f"{name}.{col} > {hi}: max {finite.max()}"


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
def test_last_row_finite_after_warmup(name):
    # On a 400-bar frame every indicator should be fully warmed up by the last bar.
    out = INDICATORS.create(name).compute(LONG)
    assert np.isfinite(out.iloc[-1].to_numpy()).all(), out.iloc[-1].to_dict()


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
def test_has_nan_warmup_for_windowed(name):
    # Window/period indicators must NOT produce a value on bar 0 (they need history).
    ind = INDICATORS.create(name)
    if ind.primary_param not in {"period", "window", "k"}:
        pytest.skip(f"{name} has no simple window warm-up")
    out = ind.compute(LONG)
    assert out.iloc[0].isna().all(), f"{name} produced a value on bar 0 (look-ahead?)"
