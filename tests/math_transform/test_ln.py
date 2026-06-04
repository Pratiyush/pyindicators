"""Natural log (ln) — golden / closed-form + domain edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.math_transform.ln import ln  # noqa: F401  (import fires @register)


def test_ln_golden_known_points():
    # ln(1) = 0, ln(e) = 1, ln(e**2) = 2, ln(10) = 2.302585...
    close = [1.0, np.e, np.e**2, 10.0]
    out = INDICATORS.create("ln").compute(frame(close))["ln"]
    np.testing.assert_allclose(out.to_numpy(), [0.0, 1.0, 2.0, np.log(10.0)], atol=1e-12)


def test_ln_matches_numpy_on_positive_series():
    df = deterministic_frame(200)  # generator keeps close >= 1.0, so all in-domain
    out = INDICATORS.create("ln").compute(df)["ln"]
    np.testing.assert_allclose(out.to_numpy(), np.log(df["close"].to_numpy()), rtol=1e-12)
    assert np.isfinite(out.to_numpy()).all()


def test_ln_negative_is_nan_zero_at_boundary():
    # x < 0 has no real log; x == 0 is the singularity. Both are guarded to NaN.
    out = INDICATORS.create("ln").compute(frame([5.0, 0.0, -3.0, 1.0]))["ln"]
    assert np.isfinite(out.iloc[0]) and np.isfinite(out.iloc[3])
    assert np.isnan(out.iloc[1]) and np.isnan(out.iloc[2])


def test_ln_log_difference_is_log_return():
    # A core use: diff of ln(close) is the log return; check against the closed form.
    df = frame([100.0, 110.0, 99.0, 105.0])
    out = INDICATORS.create("ln").compute(df)["ln"]
    expected = np.log(df["close"].to_numpy()[1:] / df["close"].to_numpy()[:-1])
    np.testing.assert_allclose(out.diff().to_numpy()[1:], expected, rtol=1e-12)


def test_ln_no_warmup_and_contract():
    df = frame([2.0, 4.0, 8.0])
    out = INDICATORS.create("ln").compute(df)
    assert list(out.columns) == ["ln"]
    assert len(out) == len(df)  # length preserved, no leading NaN warm-up
    assert str(out["ln"].dtype) == "float64"
    np.testing.assert_allclose(out["ln"].to_numpy(), np.log([2.0, 4.0, 8.0]), atol=1e-12)


def test_ln_single_row():
    out = INDICATORS.create("ln").compute(frame([np.e]))["ln"]
    assert out.size == 1
    np.testing.assert_allclose(out.to_numpy(), [1.0], atol=1e-12)
