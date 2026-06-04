"""Vector Arithmetic Div parity vs TA-Lib ``DIV`` — synthetic and real data.

DIV is a pointwise binary op with no lookback, so parity is exact (rtol=0, atol=0) over the
full finite overlap. OHLCV ``low`` is strictly positive, so our zero-denominator guard (NaN vs
TA-Lib's ``inf``) never fires here; that divergence is covered in the golden tests instead. The
finite mask additionally excludes any non-overlapping non-finite values.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.math_transform.div import div  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _p(our, ref, *, rtol=0.0, atol=0.0, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_div_parity_synthetic():
    df = deterministic_frame()
    _p(
        INDICATORS.create("div").compute(df)["div"],
        talib.DIV(df["high"].to_numpy(), df["low"].to_numpy()),
    )


def test_div_parity_real():
    df = real_frame()
    _p(
        INDICATORS.create("div").compute(df)["div"],
        talib.DIV(df["high"].to_numpy(), df["low"].to_numpy()),
    )
