"""Fisher Transform / RVGI — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_fisher_signal_is_lagged_line():
    out = INDICATORS.create("fisher", length=9, signal=1).compute(deterministic_frame(120))
    np.testing.assert_allclose(
        out["fisher_signal"].to_numpy(), out["fisher"].shift(1).to_numpy(), equal_nan=True
    )


def test_fisher_short_frame_all_nan():
    out = INDICATORS.create("fisher", length=9).compute(frame([1.0, 2.0, 3.0]))
    assert out["fisher"].isna().all()


def test_fisher_rises_on_uptrend():
    rng = np.arange(1.0, 60.0)
    out = INDICATORS.create("fisher", length=9).compute(frame(rng, high=rng + 0.5, low=rng - 0.5))
    assert out["fisher"].iloc[-1] > 0  # sustained up-move -> positive Fisher


def test_rvgi_hist_is_line_minus_signal():
    out = INDICATORS.create("rvgi").compute(deterministic_frame(120))
    np.testing.assert_allclose(
        out["rvgi_hist"].to_numpy(),
        (out["rvgi"] - out["rvgi_signal"]).to_numpy(),
        equal_nan=True,
    )


def test_rvgi_short_frame_all_nan():
    out = INDICATORS.create("rvgi", length=14).compute(frame([1.0, 2.0, 3.0]))
    assert out["rvgi"].isna().all()


def test_rvgi_flat_high_low_is_nan():
    # high == low every bar -> zero range denominator -> guarded to NaN
    flat = np.full(60, 5.0)
    out = INDICATORS.create("rvgi").compute(frame(flat, high=flat, low=flat, open_=flat))
    assert out["rvgi"].dropna().empty
