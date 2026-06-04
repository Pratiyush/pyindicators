"""Vector Arithmetic Mult parity vs TA-Lib ``MULT`` — synthetic and real data.

TA-Lib MULT is an exact element-wise product (no smoothing/seed/window), so parity is exact:
no warm-up NaNs and bit-for-bit equal finite values over the overlap.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.math_transform.mult import mult  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _p(our, ref, *, rtol=0.0, atol=0.0, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_mult_parity_synthetic():
    df = deterministic_frame()
    _p(
        INDICATORS.create("mult").compute(df)["mult"],
        talib.MULT(df["high"].to_numpy(), df["low"].to_numpy()),
    )


def test_mult_parity_real():
    df = real_frame()
    _p(
        INDICATORS.create("mult").compute(df)["mult"],
        talib.MULT(df["high"].to_numpy(), df["low"].to_numpy()),
    )
