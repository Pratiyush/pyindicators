"""OBV, ADL, CMF, Chaikin Oscillator, MFI — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_obv_known_sequence():
    f = frame([1.0, 2.0, 3.0, 2.0, 2.0], volume=[10, 10, 10, 10, 10])
    obv = INDICATORS.create("obv").compute(f)["obv"]
    # seed=vol0=10, then +,+,-,0 -> 10,20,30,20,20
    np.testing.assert_allclose(obv.to_numpy(), [10.0, 20.0, 30.0, 20.0, 20.0])


def test_ad_close_at_extremes():
    # close at high -> MFM +1 -> +vol; close at low -> MFM -1 -> -vol; H==L -> 0
    f = frame([10.0, 0.0, 5.0], high=[10.0, 10.0, 5.0], low=[0.0, 0.0, 5.0], volume=[100, 100, 100])
    ad = INDICATORS.create("ad").compute(f)["ad"]
    np.testing.assert_allclose(ad.to_numpy(), [100.0, 0.0, 0.0])  # +100, then -100 (cum 0), then +0


def test_cmf_within_bounds_and_flat():
    out = INDICATORS.create("cmf", length=20).compute(deterministic_frame(200))["cmf"]
    v = out.dropna().to_numpy()
    assert ((v >= -1 - 1e-9) & (v <= 1 + 1e-9)).all()
    flat = INDICATORS.create("cmf", length=5).compute(
        frame([5.0] * 12, high=[5.0] * 12, low=[5.0] * 12, volume=[0] * 12)
    )["cmf"]
    assert flat.dropna().eq(0).all() or flat.isna().all()  # zero MFV / zero volume


def test_adosc_finite_on_real_data():
    out = INDICATORS.create("adosc").compute(deterministic_frame(120))["adosc"]
    assert np.isfinite(out.iloc[-1])


def test_mfi_monotone_up_is_100_and_bounds():
    c = np.arange(1, 40.0)
    out = INDICATORS.create("mfi", length=5).compute(frame(c, high=c, low=c, volume=np.ones(39) * 100))["mfi"]
    np.testing.assert_allclose(out.dropna().iloc[-3:], 100.0)  # only positive money flow


def test_mfi_within_bounds():
    out = INDICATORS.create("mfi").compute(deterministic_frame(200))["mfi"]
    v = out.dropna().to_numpy()
    assert ((v >= 0) & (v <= 100)).all()
