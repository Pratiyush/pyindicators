"""ATAN — golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.math_transform.atan import atan  # noqa: F401  (import fires @register)


def test_atan_golden_known_angles():
    # atan(0)=0, atan(1)=pi/4, atan(-1)=-pi/4, atan(sqrt(3))=pi/3, atan(1/sqrt(3))=pi/6.
    c = [0.0, 1.0, -1.0, np.sqrt(3.0), 1.0 / np.sqrt(3.0)]
    out = INDICATORS.create("atan").compute(frame(c))["atan"]
    expected = [0.0, np.pi / 4, -np.pi / 4, np.pi / 3, np.pi / 6]
    np.testing.assert_allclose(out.to_numpy(), expected, atol=1e-12)


def test_atan_matches_numpy_elementwise():
    df = deterministic_frame(200)
    out = INDICATORS.create("atan").compute(df)["atan"]
    np.testing.assert_allclose(out.to_numpy(), np.arctan(df["close"].to_numpy()), atol=1e-12)


def test_atan_no_warmup_full_length_finite():
    df = deterministic_frame(50)
    out = INDICATORS.create("atan").compute(df)["atan"]
    assert len(out) == len(df)
    assert out.notna().all()  # no warm-up: every bar is defined


def test_atan_constant_input_constant_output():
    out = INDICATORS.create("atan").compute(frame([5.0, 5.0, 5.0, 5.0]))["atan"]
    np.testing.assert_allclose(out.to_numpy(), np.arctan(5.0), atol=1e-12)


def test_atan_short_frame_ok():
    out = INDICATORS.create("atan").compute(frame([1.0]))["atan"]
    assert len(out) == 1
    np.testing.assert_allclose(out.to_numpy(), [np.pi / 4], atol=1e-12)


def test_atan_bounded_open_interval():
    # Large magnitudes approach but never exceed +/- pi/2 (the declared bounds).
    out = INDICATORS.create("atan").compute(frame([1e6, -1e6, 1e9]))["atan"]
    v = out.to_numpy()
    assert (np.abs(v) < np.pi / 2).all()
    np.testing.assert_allclose(v, [np.pi / 2, -np.pi / 2, np.pi / 2], atol=1e-5)


def test_atan_is_odd_function():
    df = deterministic_frame(120)
    pos = INDICATORS.create("atan").compute(df)["atan"].to_numpy()
    neg = INDICATORS.create("atan").compute(frame(-df["close"].to_numpy()))["atan"].to_numpy()
    np.testing.assert_allclose(neg, -pos, atol=1e-12)
