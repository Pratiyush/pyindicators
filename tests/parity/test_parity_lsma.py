"""LSMA parity vs TA-Lib ``LINEARREG`` and pandas-ta ``linreg`` — synthetic and real data.

LSMA is the linear-regression endpoint value, so both references match to machine precision
(no EMA/Wilder seeding involved) on the finite overlap.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")
pta = pytest.importorskip("pandas_ta_classic")


def _p(our, ref, *, rtol=1e-9, atol=1e-7, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_lsma_parity_talib_synthetic():
    df = deterministic_frame()
    _p(INDICATORS.create("lsma", length=14).compute(df)["lsma"],
       talib.LINEARREG(df["close"].to_numpy(), 14))


def test_lsma_parity_talib_real():
    df = real_frame()
    _p(INDICATORS.create("lsma", length=14).compute(df)["lsma"],
       talib.LINEARREG(df["close"].to_numpy(), 14))


def test_lsma_parity_pta_synthetic():
    df = deterministic_frame()
    _p(INDICATORS.create("lsma", length=14).compute(df)["lsma"],
       pta.linreg(df["close"], length=14))


def test_lsma_parity_pta_real():
    df = real_frame()
    _p(INDICATORS.create("lsma", length=14).compute(df)["lsma"],
       pta.linreg(df["close"], length=14))
