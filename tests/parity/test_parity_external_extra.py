"""External-library parity for indicators whose only prior parity was definitional.

Each indicator here previously had a self-reimplementation test only; this adds a genuine
*external* oracle (tulipy or pandas-ta) so every non-bespoke indicator carries at least one
independent-library cross-check. tulipy trims its warm-up, so its output is left-padded.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import real_frame
from pyindicators import INDICATORS

DF = real_frame()
H, L, C = DF["high"], DF["low"], DF["close"]
HA, LA, CA = H.to_numpy(), L.to_numpy(), C.to_numpy()
N = len(DF)


def _close(our, ref, *, rtol=1e-6, atol=1e-6, tail=200, min_overlap=60, pad=False):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    if pad:
        ref = np.concatenate([np.full(N - len(ref), np.nan), ref])
    a, b = our[-tail:], ref[-tail:]
    mask = np.isfinite(a) & np.isfinite(b)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(a[mask], b[mask], rtol=rtol, atol=atol)


def test_rolling_high_tulipy():
    ti = pytest.importorskip("tulipy")
    _close(INDICATORS.create("rolling_high", length=50).compute(DF)["rolling_high"],
           ti.max(HA, 50), pad=True, min_overlap=120)


def test_rolling_low_tulipy():
    ti = pytest.importorskip("tulipy")
    _close(INDICATORS.create("rolling_low", length=50).compute(DF)["rolling_low"],
           ti.min(LA, 50), pad=True, min_overlap=120)


def test_keltner_pandas_ta():
    pta = pytest.importorskip("pandas_ta_classic")
    ref = pta.kc(H, L, C, length=20, scalar=2).iloc[:, 2]  # upper band
    _close(INDICATORS.create("keltner", length=20, atr_length=10, mult=2.0).compute(DF)["kc_upper"],
           ref, rtol=1e-3, atol=1e-3)


def test_quantile_pandas_ta():
    pta = pytest.importorskip("pandas_ta_classic")
    ref = pta.quantile(C, length=30, q=0.5)
    _close(INDICATORS.create("quantile", length=30, q=0.5).compute(DF)["quantile"], ref,
           rtol=1e-9, atol=1e-9)


def test_lag_tulipy():
    ti = pytest.importorskip("tulipy")
    _close(INDICATORS.create("lag", length=1).compute(DF)["lag"], ti.lag(CA, 1),
           pad=True, rtol=1e-12, atol=1e-12, min_overlap=120)
