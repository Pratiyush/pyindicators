"""ASIN parity vs TA-Lib ``ASIN`` — synthetic and real data.

TA-Lib applies ASIN directly to the input series (no normalisation), so raw OHLCV closes
(prices >> 1) are all out of domain and yield only NaN. To exercise the in-domain math on
genuine price *shape*, we rescale each frame's close into [-1, 1] and feed the SAME series to
both our indicator and ``talib.ASIN`` — a faithful element-wise comparison either way.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

talib = pytest.importorskip("talib")


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=200):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _normalized(df):
    """Rescale close into [-1, 1] (min->-1, max->+1) so ASIN's domain is fully covered."""
    out = df.copy()
    c = out["close"].to_numpy(dtype="float64")
    out["close"] = 2.0 * (c - c.min()) / (c.max() - c.min()) - 1.0
    return out


def test_asin_parity_synthetic():
    df = _normalized(deterministic_frame())
    _p(INDICATORS.create("asin").compute(df)["asin"], talib.ASIN(df["close"]))


def test_asin_parity_real():
    df = _normalized(real_frame())
    _p(INDICATORS.create("asin").compute(df)["asin"], talib.ASIN(df["close"]))


def test_asin_parity_out_of_domain_both_nan():
    # On raw (out-of-domain) prices both implementations agree: all NaN.
    df = real_frame()
    ours = INDICATORS.create("asin").compute(df)["asin"].to_numpy()
    ref = np.asarray(talib.ASIN(df["close"]), dtype="float64")
    assert np.isnan(ours).all() and np.isnan(ref).all()
