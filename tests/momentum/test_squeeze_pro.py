"""TTM Squeeze Pro — golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.momentum.squeeze_pro import squeeze_pro  # noqa: F401  (fires @register)

FLAGS = ("sqz_on_wide", "sqz_on_normal", "sqz_on_narrow", "sqz_off", "sqz_no")
OUTPUTS = ("sqz", *FLAGS)


def test_output_contract():
    out = INDICATORS.create("squeeze_pro").compute(deterministic_frame(200))
    assert list(out.columns) == list(OUTPUTS)
    assert len(out) == 200
    assert (out.dtypes == "float64").all()
    # Flags are exactly 0/1 everywhere (warm-up NaN comparisons collapse to False -> 0).
    for col in FLAGS:
        assert set(np.unique(out[col].to_numpy())) <= {0.0, 1.0}


def test_flags_are_one_hot_partition():
    # On the wide tier exactly one of {on_wide, off_wide, no} holds each bar, and the
    # narrower tiers nest inside the wide on-squeeze.
    out = INDICATORS.create("squeeze_pro").compute(deterministic_frame(300))
    partition = out["sqz_on_wide"] + out["sqz_off"] + out["sqz_no"]
    assert (partition == 1.0).all()
    assert (out["sqz_on_narrow"] <= out["sqz_on_normal"]).all()
    assert (out["sqz_on_normal"] <= out["sqz_on_wide"]).all()


def test_flat_close_with_range_forces_full_squeeze():
    # Constant close -> BB collapses to the basis (stdev 0); a fixed high/low spread keeps
    # KC open (TR > 0), so BB sits strictly inside every KC tier -> all three squeezes ON.
    n = 60
    df = frame(np.full(n, 100.0), high=np.full(n, 101.0), low=np.full(n, 99.0))
    out = INDICATORS.create("squeeze_pro").compute(df).iloc[-1]
    assert out["sqz_on_wide"] == 1.0
    assert out["sqz_on_normal"] == 1.0
    assert out["sqz_on_narrow"] == 1.0
    assert out["sqz_off"] == 0.0
    assert out["sqz_no"] == 0.0
    assert out["sqz"] == 0.0  # diff of a constant is 0 -> smoothed momentum is 0


def test_fully_flat_series_is_no_squeeze():
    # No range at all: BB and KC both collapse onto the basis, so neither strict inequality
    # holds -> sqz_no = 1 (the guard against a fabricated squeeze on a dead market).
    out = INDICATORS.create("squeeze_pro").compute(frame(np.full(50, 100.0))).iloc[-1]
    assert out["sqz_no"] == 1.0
    assert out["sqz_on_wide"] == 0.0
    assert out["sqz_off"] == 0.0
    assert out["sqz"] == 0.0


def test_momentum_on_linear_ramp_equals_mom_length():
    # On a unit-slope line close.diff(mom_length) == mom_length (constant), so the SMA of it
    # is exactly mom_length once warmed up.
    out = INDICATORS.create("squeeze_pro", mom_length=12, mom_smooth=6).compute(
        frame(np.arange(1.0, 61.0))
    )["sqz"]
    np.testing.assert_allclose(out.dropna().to_numpy(), 12.0, atol=1e-9)
    # Warm-up is mom_length + mom_smooth - 1 = 17 leading NaNs.
    assert out.isna().sum() == 17


def test_short_frame_momentum_nan_flags_no_squeeze():
    # Fewer bars than the warm-up: momentum is all NaN, yet flags stay 0/1 with sqz_no = 1.
    out = INDICATORS.create("squeeze_pro").compute(frame([1.0, 2.0, 3.0]))
    assert out["sqz"].isna().all()
    assert (out["sqz_no"] == 1.0).all()
    for col in ("sqz_on_wide", "sqz_on_normal", "sqz_on_narrow", "sqz_off"):
        assert (out[col] == 0.0).all()


def test_rejects_nondescending_scalars():
    import pytest

    with pytest.raises(ValueError):
        INDICATORS.create("squeeze_pro", kc_scalar_wide=1.0, kc_scalar_normal=1.5)


def test_rejects_unknown_param():
    import pytest

    with pytest.raises(ValueError):
        INDICATORS.create("squeeze_pro", bogus=1)
