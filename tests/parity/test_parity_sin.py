"""SIN parity vs TA-Lib — synthetic and real data.

TA-Lib ``SIN`` is an exact element-wise transform (identical to ``numpy.sin``), so there is no
warm-up / seeding convergence: we can assert with very tight tolerances over the whole finite
overlap (no tail trimming needed). We also pin the closed-form ``numpy.sin`` oracle directly so
the parity holds even if TA-Lib is not installed.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS


def _p(our, ref, *, rtol=1e-12, atol=1e-12, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_sin_oracle_synthetic():
    # Closed-form oracle (numpy.sin) — runs even without TA-Lib installed.
    df = deterministic_frame()
    _p(INDICATORS.create("sin").compute(df)["sin"], np.sin(df["close"].to_numpy()))


def test_sin_oracle_real():
    df = real_frame()
    _p(INDICATORS.create("sin").compute(df)["sin"], np.sin(df["close"].to_numpy()))


def test_sin_parity_talib_synthetic():
    talib = pytest.importorskip("talib")
    df = deterministic_frame()
    _p(INDICATORS.create("sin").compute(df)["sin"], talib.SIN(df["close"].to_numpy()))


def test_sin_parity_talib_real():
    talib = pytest.importorskip("talib")
    df = real_frame()
    _p(INDICATORS.create("sin").compute(df)["sin"], talib.SIN(df["close"].to_numpy()))
