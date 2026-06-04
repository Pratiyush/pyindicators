"""MAMA parity vs TA-Lib ``MAMA`` (first output) — synthetic and real data.

The Ehlers Hilbert pipeline plus the phase-rate adaptive EMA reproduces TA-Lib's MAMA line.
The recurrence seeds at bar 6 (TA-Lib emits from the 32-bar lookback), so the warm-up just
after the lookback is a transient that converges to TA-Lib once the seeded EMAs lose memory
of their ``prev = 0`` start — hence the parity is checked on the tail (max rel |Δ| ~5e-10 on
both frames). The NaN-before-lookback positions match TA-Lib exactly everywhere.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.trend.mama import mama  # noqa: F401 — import so @register fires

talib = pytest.importorskip("talib")

_TAIL = 200  # bars from the end where the seeded MAMA/FAMA EMAs have settled onto TA-Lib


def _parity(df):
    out = INDICATORS.create("mama").compute(df)
    ours = out["mama"].to_numpy(dtype="float64")
    ref, _ = talib.MAMA(df["close"].to_numpy(), 0.5, 0.05)
    ref = np.asarray(ref, dtype="float64")
    # NaN convention (warm-up masking) must match TA-Lib exactly.
    assert np.array_equal(np.isnan(ours), np.isnan(ref))
    o, r = ours[-_TAIL:], ref[-_TAIL:]
    mask = np.isfinite(o) & np.isfinite(r)
    assert mask.sum() >= _TAIL // 2
    np.testing.assert_allclose(o[mask], r[mask], rtol=1e-6, atol=1e-6)


def test_mama_parity_synthetic():
    _parity(deterministic_frame())


def test_mama_parity_real():
    _parity(real_frame())
