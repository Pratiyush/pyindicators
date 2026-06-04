"""VWAP, Force Index, Ease of Movement, PVT — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_vwap_constant_price():
    out = INDICATORS.create("vwap", length=5).compute(frame([7.0] * 12, volume=np.arange(1, 13.0)))
    np.testing.assert_allclose(out["vwap"].dropna(), 7.0)


def test_efi_flat_is_zero():
    out = INDICATORS.create("efi", length=5).compute(frame([5.0] * 20, volume=[100] * 20))
    np.testing.assert_allclose(out["efi"].dropna(), 0.0)  # no price change -> zero force


def test_eom_flat_range_is_nan():
    f = frame([5.0] * 20, high=[5.0] * 20, low=[5.0] * 20, volume=[100] * 20)
    assert INDICATORS.create("eom", length=5).compute(f)["eom"].isna().all()  # H==L


def test_eom_finite_on_real_data():
    out = INDICATORS.create("eom").compute(deterministic_frame(100))["eom"]
    assert np.isfinite(out.iloc[-1])


def test_pvt_known_sequence():
    f = frame([100.0, 110.0, 99.0], volume=[10, 10, 10])
    pvt = INDICATORS.create("pvt").compute(f)["pvt"]
    # pct=[seed0, +0.1, -0.1] * vol -> delta=[0, 1.0, -1.0] -> cumsum [0, 1.0, 0.0]
    np.testing.assert_allclose(pvt.to_numpy(), [0.0, 1.0, 0.0], atol=1e-9)
