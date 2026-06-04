"""Finite Volume Element — golden/closed-form + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.volume.fve import fve  # noqa: F401  (import fires @register for self-verify)


def test_fve_rising_line_closed_form():
    # H=L=C rising +1/bar with factor=0 => mf = diff(close) = +1 > 0 every bar; the warm-up
    # NaN signs to 0. With volume==1 and length=3, signed = [0,1,1,1,...] so FVE = rollsum3/3*100:
    # idx2 = (0+1+1)/3*100, idx>=3 = 100.
    out = INDICATORS.create("fve", length=3, factor=0.0).compute(frame(np.arange(10.0, 20.0)))["fve"]
    v = out.to_numpy()
    assert np.isnan(v[0]) and np.isnan(v[1])
    np.testing.assert_allclose(v[2], 200.0 / 3.0)
    np.testing.assert_allclose(v[3:], 100.0)


def test_fve_falling_line_closed_form():
    # Mirror image: H=L=C falling -1/bar, factor=0 => mf < 0 => signed = -volume => FVE goes to -100.
    out = INDICATORS.create("fve", length=3, factor=0.0).compute(
        frame(np.arange(20.0, 10.0, -1.0))
    )["fve"]
    v = out.to_numpy()
    np.testing.assert_allclose(v[2], -200.0 / 3.0)
    np.testing.assert_allclose(v[3:], -100.0)


def test_fve_flat_series_is_zero():
    # Fully flat frame: mf == 0, so it never clears the deadband -> signed 0 -> FVE 0 (avg vol
    # is nonzero here, so safe_divide does NOT fire).
    out = INDICATORS.create("fve", length=3, factor=0.0).compute(frame(np.full(8, 50.0)))["fve"]
    np.testing.assert_allclose(out.to_numpy()[2:], 0.0)


def test_fve_deadband_suppresses_small_moves():
    # close~100, factor=0.3 => cutoff = 0.3*100/100 = 0.3. Steps of +0.1 sit inside the band,
    # so every bar signs 0 and FVE stays 0; bumping the step past 0.3 reactivates accumulation.
    inside = INDICATORS.create("fve", length=3, factor=0.3).compute(
        frame(100.0 + np.arange(8) * 0.1)
    )["fve"]
    np.testing.assert_allclose(inside.to_numpy()[2:], 0.0)
    outside = INDICATORS.create("fve", length=3, factor=0.3).compute(
        frame(100.0 + np.arange(8) * 0.5)
    )["fve"]
    np.testing.assert_allclose(outside.to_numpy()[3:], 100.0)


def test_fve_zero_volume_guarded_to_nan():
    # avg_volume == 0 => denominator (avg_volume*length) == 0 => safe_divide yields NaN, not inf.
    df = frame(np.arange(10.0, 18.0), volume=np.zeros(8))
    out = INDICATORS.create("fve", length=3, factor=0.0).compute(df)["fve"]
    assert out.isna().all()


def test_fve_short_frame_all_nan():
    # Fewer bars than length => the rolling sum/mean never reach min_periods => all NaN.
    out = INDICATORS.create("fve", length=22, factor=0.3).compute(frame([1.0, 2.0, 3.0]))["fve"]
    assert out.isna().all()


def test_fve_length_one_window():
    # length=1 has no warm-up: signed_volume / (volume * 1) * 100. The first bar's mf is NaN ->
    # signs to 0 -> 0/vol*100 == 0; every later (rising) bar is +volume -> +100.
    out = INDICATORS.create("fve", length=1, factor=0.0).compute(frame(np.arange(10.0, 16.0)))["fve"]
    v = out.to_numpy()
    np.testing.assert_allclose(v[0], 0.0)
    np.testing.assert_allclose(v[1:], 100.0)


def test_fve_finite_and_varies_on_real_trend():
    out = INDICATORS.create("fve", length=22, factor=0.3).compute(deterministic_frame(300))["fve"]
    finite = out.dropna().to_numpy()
    assert finite.size > 200 and finite.std() > 0


def test_fve_output_contract():
    df = deterministic_frame(120)
    out = INDICATORS.create("fve", length=22).compute(df)
    assert list(out.columns) == ["fve"]
    assert len(out) == len(df)
    assert out["fve"].dtype == np.float64
