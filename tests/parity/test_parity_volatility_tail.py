"""Volatility long-tail parity vs pandas-ta (Ulcer, Mass Index, PDIST, ACCBANDS)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")

LONG = deterministic_frame()


def _p(our, ref, *, rtol=1e-5, atol=1e-5, min_overlap=80):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_ulcer_parity():
    _p(INDICATORS.create("ulcer", length=14).compute(LONG)["ulcer"], pta.ui(LONG["close"], length=14))


def test_massi_parity():
    ref = pta.massi(LONG["high"], LONG["low"], fast=9, slow=25)
    _p(INDICATORS.create("massi").compute(LONG)["massi"], ref)


def test_pdist_parity():
    ref = pta.pdist(LONG["open"], LONG["high"], LONG["low"], LONG["close"], drift=1)
    _p(INDICATORS.create("pdist").compute(LONG)["pdist"], ref)


def test_accbands_parity():
    df = pta.accbands(LONG["high"], LONG["low"], LONG["close"], length=20)
    out = INDICATORS.create("accbands", length=20).compute(LONG)
    _p(out["accbands_lower"], df.iloc[:, 0])
    _p(out["accbands_mid"], df.iloc[:, 1])
    _p(out["accbands_upper"], df.iloc[:, 2])
