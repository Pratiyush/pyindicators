"""Arccosine — golden / closed-form + domain-guard edge cases."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.math_transform.acos import acos  # noqa: F401  (import fires @register)


def test_acos_closed_form_landmarks():
    # Exact landmark angles: acos(1)=0, acos(0)=pi/2, acos(-1)=pi (no warm-up, per-bar map).
    out = INDICATORS.create("acos").compute(frame([1.0, np.sqrt(3) / 2, 0.5, 0.0, -1.0]))["acos"]
    expected = [0.0, np.pi / 6, np.pi / 3, np.pi / 2, np.pi]
    np.testing.assert_allclose(out.to_numpy(), expected, rtol=0, atol=1e-12)


def test_acos_matches_numpy_in_domain():
    # On an in-domain ramp, acos equals numpy.arccos exactly (this is the primitive).
    closes = np.linspace(-1.0, 1.0, 50)
    out = INDICATORS.create("acos").compute(frame(closes))["acos"]
    np.testing.assert_allclose(out.to_numpy(), np.arccos(closes), rtol=0, atol=0)


def test_acos_out_of_domain_is_nan():
    # Real arccos is undefined for |x| > 1 -> guarded to NaN (not forced/complex), both ends.
    out = INDICATORS.create("acos").compute(frame([-2.0, -1.5, -1.0, 0.0, 1.0, 1.5, 2.0]))["acos"]
    res = out.to_numpy()
    assert np.isnan(res[[0, 1, 5, 6]]).all()  # |x| > 1 -> NaN
    np.testing.assert_allclose(res[[2, 3, 4]], [np.pi, np.pi / 2, 0.0], rtol=0, atol=1e-12)


def test_acos_propagates_nan():
    out = INDICATORS.create("acos").compute(frame([0.5, np.nan, -0.5]))["acos"]
    res = out.to_numpy()
    assert np.isnan(res[1])
    np.testing.assert_allclose(res[[0, 2]], [np.arccos(0.5), np.arccos(-0.5)], rtol=0, atol=0)


def test_acos_constant_input_is_constant():
    # A flat in-domain series maps to a flat angle (stateless, no path dependence).
    out = INDICATORS.create("acos").compute(frame([0.25, 0.25, 0.25, 0.25]))["acos"]
    np.testing.assert_allclose(out.to_numpy(), np.full(4, np.arccos(0.25)), rtol=0, atol=0)


def test_acos_within_declared_bounds():
    # Output stays in [0, pi] across the whole valid domain.
    out = INDICATORS.create("acos").compute(frame(np.linspace(-1.0, 1.0, 101)))["acos"]
    v = out.to_numpy()
    assert (v >= 0.0 - 1e-12).all() and (v <= np.pi + 1e-12).all()


def test_acos_length_and_dtype_preserved():
    # Output length == input length, float64, single 'acos' column, same index.
    df = frame([0.1, 0.2, 0.3])
    res = INDICATORS.create("acos").compute(df)
    assert list(res.columns) == ["acos"]
    assert res["acos"].dtype == np.float64
    assert len(res) == len(df)
    pd.testing.assert_index_equal(res.index, df.index)


def test_acos_short_frame_no_warmup():
    # No window => a single in-domain bar already has a value (unlike windowed indicators).
    out = INDICATORS.create("acos").compute(frame([1.0]))["acos"]
    assert out.notna().all()
    assert out.iloc[0] == 0.0


def test_acos_takes_no_params():
    # Parameter-free element-wise op: passing a param must be rejected by Params/contract.
    try:
        INDICATORS.create("acos", length=14)
    except (TypeError, ValueError):
        return
    raise AssertionError("acos should not accept parameters")
