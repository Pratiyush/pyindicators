"""Volume Flow Indicator — golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.volume.vfi import vfi  # noqa: F401 -- import fires @register for self-verify


def test_vfi_flat_typical_price_is_zero():
    # H==L==C constant -> typical change 0 and volatility cutoff 0 -> no bar qualifies as up
    # or down volume (multiplier 0 everywhere) -> the running sum, hence VFI, is exactly 0.
    n = 200
    c = np.full(n, 50.0)
    out = INDICATORS.create("vfi").compute(
        frame(c, high=c, low=c, volume=np.arange(1.0, n + 1.0))
    )["vfi"]
    finite = out.dropna().to_numpy()
    assert finite.size > 0
    np.testing.assert_allclose(finite, 0.0, atol=1e-12)


def test_vfi_short_frame_all_nan():
    # Fewer bars than ``period`` -> the period-length rolling sum never fills -> all NaN.
    out = INDICATORS.create("vfi", period=130).compute(deterministic_frame(120))["vfi"]
    assert out.isna().all()


def test_vfi_warmup_then_finite():
    # period=130: first finite value lands at index 131 (130-bar sum + the mav.shift(1) lag);
    # everything before is warm-up NaN, everything after is finite.
    out = INDICATORS.create("vfi", period=130).compute(deterministic_frame(400))["vfi"]
    v = out.to_numpy()
    first = np.flatnonzero(np.isfinite(v))
    assert first.size > 0 and first[0] == 131
    assert np.isfinite(v[131:]).all()


def test_vfi_finite_and_varies_on_real_trend():
    out = INDICATORS.create("vfi").compute(deterministic_frame(400))["vfi"]
    v = out.dropna().to_numpy()
    assert v.size > 100 and np.isfinite(v).all() and v.std() > 0


def test_vfi_zero_volume_is_guarded_nan():
    # All-zero volume -> average volume 0 -> the normaliser division is guarded to NaN
    # (never +/-inf), so the output is entirely NaN rather than blowing up.
    n = 200
    c = np.maximum(50.0 + np.cumsum(np.ones(n)), 1.0)
    out = INDICATORS.create("vfi").compute(
        frame(c, high=c * 1.01, low=c * 0.99, volume=np.zeros(n))
    )["vfi"]
    assert out.isna().all()


def test_vfi_output_contract():
    out = INDICATORS.create("vfi").compute(deterministic_frame(300))
    assert list(out.columns) == ["vfi"]
    assert out["vfi"].dtype == np.float64
    assert len(out) == 300
