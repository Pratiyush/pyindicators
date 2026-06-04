"""Sub parity vs TA-Lib ``SUB`` — synthetic and real data.

TA-Lib ``SUB(real0, real1)`` is element-wise ``real0 - real1`` with lookback 0. Our ``sub``
wires (high, low) into (real0, real1), so we compare directly against
``talib.SUB(high, low)`` — a closed form (no smoothing/seed drift), hence bit-for-bit exact
on the full finite overlap.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.math_transform.sub import sub  # noqa: F401  (fires @register)

talib = pytest.importorskip("talib")


def _p(our, ref, *, rtol=0.0, atol=0.0, min_overlap=200):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_sub_parity_synthetic():
    df = deterministic_frame()
    _p(
        INDICATORS.create("sub").compute(df)["sub"],
        talib.SUB(df["high"].to_numpy(), df["low"].to_numpy()),
    )


def test_sub_parity_real():
    df = real_frame()
    _p(
        INDICATORS.create("sub").compute(df)["sub"],
        talib.SUB(df["high"].to_numpy(), df["low"].to_numpy()),
    )
