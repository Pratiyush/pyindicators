"""FAMA parity vs TA-Lib ``MAMA`` (second output) — synthetic and real data.

FAMA is the slow companion line of TA-Lib's MAMA. Like MAMA it seeds at bar 6 and emits from
the 32-bar lookback, so the warm-up after the lookback is a transient that converges to
TA-Lib on the tail (max rel |Δ| ~5e-10 on both frames); the NaN-before-lookback positions
match TA-Lib exactly.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.trend.fama import fama  # noqa: F401 — import so @register fires

talib = pytest.importorskip("talib")

_TAIL = 200  # bars from the end where the seeded FAMA EMA has settled onto TA-Lib


def _parity(df):
    ours = INDICATORS.create("fama").compute(df)["fama"].to_numpy(dtype="float64")
    _, ref = talib.MAMA(df["close"].to_numpy(), 0.5, 0.05)
    ref = np.asarray(ref, dtype="float64")
    # NaN convention (warm-up masking) must match TA-Lib exactly.
    assert np.array_equal(np.isnan(ours), np.isnan(ref))
    o, r = ours[-_TAIL:], ref[-_TAIL:]
    mask = np.isfinite(o) & np.isfinite(r)
    assert mask.sum() >= _TAIL // 2
    np.testing.assert_allclose(o[mask], r[mask], rtol=1e-6, atol=1e-6)


def test_fama_parity_synthetic():
    _parity(deterministic_frame())


def test_fama_parity_real():
    _parity(real_frame())
