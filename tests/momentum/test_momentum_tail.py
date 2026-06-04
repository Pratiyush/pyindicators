"""MOM, ROCP/ROCR/ROCR100, CMO, BOP, AO, Coppock — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_mom():
    out = INDICATORS.create("mom", length=1).compute(frame([1.0, 3.0, 6.0]))["mom"]
    np.testing.assert_allclose(out.to_numpy()[1:], [2.0, 3.0])


def test_roc_ratios():
    f = frame([100.0, 110.0])
    np.testing.assert_allclose(INDICATORS.create("rocp", length=1).compute(f)["rocp"].iloc[1], 0.1)
    np.testing.assert_allclose(INDICATORS.create("rocr", length=1).compute(f)["rocr"].iloc[1], 1.1)
    np.testing.assert_allclose(INDICATORS.create("rocr100", length=1).compute(f)["rocr100"].iloc[1], 110.0)


def test_cmo_extremes_and_flat():
    up = INDICATORS.create("cmo", length=5).compute(frame(np.arange(1, 20.0)))["cmo"]
    np.testing.assert_allclose(up.dropna().iloc[-3:], 100.0)
    down = INDICATORS.create("cmo", length=5).compute(frame(np.arange(20, 1, -1.0)))["cmo"]
    np.testing.assert_allclose(down.dropna().iloc[-3:], -100.0)
    flat = INDICATORS.create("cmo", length=5).compute(frame([5.0] * 12))["cmo"]
    assert flat.iloc[5:].isna().all()


def test_bop_extremes():
    # close at high, open at low -> BOP = 1; H==L -> NaN
    f = frame([10.0], high=[10.0], low=[5.0], open_=[5.0])
    np.testing.assert_allclose(INDICATORS.create("bop").compute(f)["bop"].iloc[0], 1.0)
    flat = frame([5.0, 5.0], high=[5.0, 5.0], low=[5.0, 5.0], open_=[5.0, 5.0])
    assert INDICATORS.create("bop").compute(flat)["bop"].isna().all()


def test_ao_finite():
    out = INDICATORS.create("ao").compute(deterministic_frame(100))["ao"]
    assert np.isfinite(out.iloc[-1])


def test_coppock_constant_is_zero():
    out = INDICATORS.create("coppock").compute(frame([5.0] * 60))["coppock"]
    np.testing.assert_allclose(out.dropna(), 0.0, atol=1e-9)
