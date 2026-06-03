"""Optional oracle cross-check against a reference TA library (test-only).

Skipped automatically when the oracle isn't installed, so CI stays green without it.
Install with ``uv pip install pandas-ta-classic`` (or ``pandas-ta``) to enable.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS

pt = None
for _mod in ("pandas_ta", "pandas_ta_classic"):
    try:
        pt = __import__(_mod)
        break
    except Exception:
        continue
if pt is None:
    pytest.skip("no pandas-ta oracle installed", allow_module_level=True)
DF = deterministic_frame()


def _overlap_allclose(ours, theirs, rtol, atol=1e-8):
    a, b = ours.to_numpy(), np.asarray(theirs, dtype="float64")
    mask = np.isfinite(a) & np.isfinite(b)
    assert mask.sum() > 50, "too few overlapping points to compare"
    np.testing.assert_allclose(a[mask], b[mask], rtol=rtol, atol=atol)


def test_sma_matches_oracle():
    ours = INDICATORS.create("sma", period=20).compute(DF)["sma"]
    _overlap_allclose(ours, pt.sma(DF["close"], length=20), rtol=1e-9)


def test_ema_matches_oracle():
    ours = INDICATORS.create("ema", period=20).compute(DF)["ema"]
    _overlap_allclose(ours, pt.ema(DF["close"], length=20), rtol=1e-3)


def test_rsi_matches_oracle():
    # RSI seeding/smoothing conventions vary slightly across libraries -> looser tol.
    ours = INDICATORS.create("rsi", period=14).compute(DF)["rsi"]
    _overlap_allclose(ours, pt.rsi(DF["close"], length=14), rtol=1e-2)
