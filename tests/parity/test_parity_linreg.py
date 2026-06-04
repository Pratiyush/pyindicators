"""Linear-regression family parity vs TA-Lib."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")

LONG = deterministic_frame()
C = LONG["close"].to_numpy()


def _p(our, ref, *, rtol=1e-6, atol=1e-6, min_overlap=100):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_linreg_parity():
    _p(INDICATORS.create("linreg", length=14).compute(LONG)["linreg"], talib.LINEARREG(C, 14))


def test_linreg_slope_parity():
    _p(INDICATORS.create("linreg_slope", length=14).compute(LONG)["linreg_slope"],
       talib.LINEARREG_SLOPE(C, 14))


def test_linreg_intercept_parity():
    _p(INDICATORS.create("linreg_intercept", length=14).compute(LONG)["linreg_intercept"],
       talib.LINEARREG_INTERCEPT(C, 14))


def test_linreg_angle_parity():
    _p(INDICATORS.create("linreg_angle", length=14).compute(LONG)["linreg_angle"],
       talib.LINEARREG_ANGLE(C, 14))


def test_tsf_parity():
    _p(INDICATORS.create("tsf", length=14).compute(LONG)["tsf"], talib.TSF(C, 14))
