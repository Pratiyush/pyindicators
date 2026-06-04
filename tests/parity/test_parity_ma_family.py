"""MA-family parity vs pandas-ta (VWMA/ZLMA/ALMA/FWMA/SINWMA/PWMA; not in core TA-Lib)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")

LONG = deterministic_frame()
C = LONG["close"]


def _p(our, ref, *, rtol=1e-6, atol=1e-6, min_overlap=80):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_vwma_parity():
    _p(INDICATORS.create("vwma", length=20).compute(LONG)["vwma"],
       pta.vwma(C, LONG["volume"], length=20))


def test_zlma_parity():
    _p(INDICATORS.create("zlma", length=10).compute(LONG)["zlma"], pta.zlma(C, length=10))


def test_alma_matches_canonical_formula():
    # Our ALMA follows the canonical TradingView/Legoux weighting (offset shifts weight toward
    # recent bars). pandas-ta reverses the weights (w[::-1]) — a deviation — so we validate
    # against the explicit canonical formula rather than pandas-ta here.
    length, sigma, offset = 10, 6.0, 0.85
    m, s = offset * (length - 1), length / sigma
    w = np.exp(-((np.arange(length) - m) ** 2) / (2.0 * s * s))
    w /= w.sum()
    c = LONG["close"].to_numpy()
    expected = np.full(c.size, np.nan)
    for t in range(length - 1, c.size):
        expected[t] = float(np.dot(c[t - length + 1 : t + 1], w))
    _p(INDICATORS.create("alma", length=10).compute(LONG)["alma"], expected)


def test_fwma_parity():
    _p(INDICATORS.create("fwma", length=10).compute(LONG)["fwma"], pta.fwma(C, length=10))


def test_sinwma_parity():
    _p(INDICATORS.create("sinwma", length=14).compute(LONG)["sinwma"], pta.sinwma(C, length=14))


def test_pwma_parity():
    _p(INDICATORS.create("pwma", length=10).compute(LONG)["pwma"], pta.pwma(C, length=10))
