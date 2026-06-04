"""TTM Squeeze — golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.momentum.squeeze import squeeze  # noqa: F401  (import fires @register)


def test_squeeze_outputs_and_flags_partition():
    out = INDICATORS.create("squeeze").compute(deterministic_frame(200))
    assert list(out.columns) == ["squeeze", "squeeze_on", "squeeze_off", "squeeze_no"]
    assert out.dtypes.eq("float64").all()
    # Exactly one of on/off/no is set on every bar (warm-up included).
    total = out["squeeze_on"] + out["squeeze_off"] + out["squeeze_no"]
    assert np.array_equal(total.to_numpy(), np.ones(len(out)))
    # Flags are strictly 0/1.
    for col in ("squeeze_on", "squeeze_off", "squeeze_no"):
        assert set(np.unique(out[col].to_numpy())).issubset({0.0, 1.0})


def test_squeeze_momentum_is_sma_of_mom():
    # Default momentum is SMA(MOM(close, 12), 6); assert against that closed form.
    df = deterministic_frame(200)
    out = INDICATORS.create("squeeze").compute(df)["squeeze"]
    expected = df["close"].diff(12).rolling(6).mean()
    np.testing.assert_allclose(out.to_numpy(), expected.to_numpy(), rtol=1e-12, equal_nan=True)
    # Warm-up: first valid value at index mom_length + mom_smooth - 1 = 17.
    assert out.first_valid_index() == 17
    assert out.iloc[:17].isna().all()


def test_squeeze_flat_series_no_false_squeeze():
    # A constant series collapses both envelopes onto the basis; the *strict* inequalities
    # then fail, so a flat market is classified as "no squeeze", momentum is exactly zero.
    out = INDICATORS.create("squeeze").compute(frame([50.0] * 40))
    assert (out["squeeze_on"] == 0.0).all()
    assert (out["squeeze_off"] == 0.0).all()
    assert (out["squeeze_no"] == 1.0).all()
    np.testing.assert_allclose(out["squeeze"].dropna().to_numpy(), 0.0, atol=1e-12)


def test_squeeze_short_frame_is_all_no_and_nan_momentum():
    # Fewer bars than the longest warm-up: bands never form, so every bar is "no squeeze"
    # and momentum stays NaN throughout.
    out = INDICATORS.create("squeeze").compute(frame([1.0, 2.0, 3.0, 4.0, 5.0]))
    assert out["squeeze"].isna().all()
    assert (out["squeeze_no"] == 1.0).all()
    assert (out["squeeze_on"] == 0.0).all()
    assert (out["squeeze_off"] == 0.0).all()


def test_squeeze_detects_a_real_squeeze_somewhere():
    # On a genuine random walk there must be at least one bar in each of the on / off states
    # (otherwise the classification logic is broken / always falling through to "no").
    out = INDICATORS.create("squeeze").compute(deterministic_frame(400))
    assert out["squeeze_on"].sum() > 0
    assert out["squeeze_off"].sum() > 0


def test_squeeze_custom_lengths_change_warmup():
    # Shorter momentum windows -> earlier first valid momentum value.
    df = deterministic_frame(120)
    out = INDICATORS.create("squeeze", mom_length=5, mom_smooth=3).compute(df)["squeeze"]
    assert out.first_valid_index() == 5 + 3 - 1  # 7
    expected = df["close"].diff(5).rolling(3).mean()
    np.testing.assert_allclose(out.to_numpy(), expected.to_numpy(), rtol=1e-12, equal_nan=True)


def test_squeeze_rejects_unknown_param():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        INDICATORS.create("squeeze", not_a_param=3)
