"""TAN — golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.math_transform.tan import tan  # noqa: F401  (import fires @register)


def test_tan_closed_form_known_angles():
    # tan(0)=0, tan(pi/4)=1, tan(pi)=0 (modulo float), tan(-pi/4)=-1.
    angles = [0.0, np.pi / 4.0, np.pi, -np.pi / 4.0]
    out = INDICATORS.create("tan").compute(frame(angles))["tan"]
    np.testing.assert_allclose(out.to_numpy(), np.tan(np.array(angles)), rtol=0, atol=1e-12)


def test_tan_matches_numpy_on_random_walk():
    df = deterministic_frame(200)
    out = INDICATORS.create("tan").compute(df)["tan"]
    np.testing.assert_allclose(out.to_numpy(), np.tan(df["close"].to_numpy()), rtol=0, atol=0)


def test_tan_no_warmup_full_length_and_finite():
    df = deterministic_frame(50)
    out = INDICATORS.create("tan").compute(df)["tan"]
    assert len(out) == len(df)
    assert out.notna().all()  # no warm-up NaNs for a pointwise transform
    assert str(out.dtype) == "float64"


def test_tan_constant_input_is_constant_output():
    out = INDICATORS.create("tan").compute(frame([0.7] * 8))["tan"]
    np.testing.assert_allclose(out.to_numpy(), np.full(8, np.tan(0.7)), rtol=0, atol=1e-12)


def test_tan_short_frame_single_bar():
    out = INDICATORS.create("tan").compute(frame([1.0]))["tan"]
    assert len(out) == 1
    np.testing.assert_allclose(out.to_numpy(), [np.tan(1.0)], rtol=0, atol=1e-12)


def test_tan_nan_propagates():
    out = INDICATORS.create("tan").compute(frame([np.nan, 0.0, np.nan]))["tan"]
    assert np.isnan(out.iloc[0]) and np.isnan(out.iloc[2])
    np.testing.assert_allclose(out.iloc[1], 0.0, atol=1e-12)


def test_tan_is_odd_function():
    # tan(-x) == -tan(x): a clean structural identity that pins the sign convention.
    xs = [0.3, 0.9, 1.2, 2.5]
    pos = INDICATORS.create("tan").compute(frame(xs))["tan"].to_numpy()
    neg = INDICATORS.create("tan").compute(frame([-x for x in xs]))["tan"].to_numpy()
    np.testing.assert_allclose(neg, -pos, rtol=0, atol=1e-12)


def test_tan_takes_no_params():
    out = INDICATORS.create("tan").compute(frame([0.5, 1.0]))["tan"]
    assert list(out.index) == [0, 1]
