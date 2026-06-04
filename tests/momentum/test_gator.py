"""Gator Oscillator — golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.base import rma
from pyindicators.momentum.gator import gator  # noqa: F401  (import fires @register)


def _oracle(df, jaw=13, teeth=8, lips=5):
    """Independent restatement of the spec from the unshifted Alligator lines."""
    med = (df["high"] + df["low"]) / 2.0
    j, t, lp = rma(med, jaw), rma(med, teeth), rma(med, lips)
    return (j - t).abs().to_numpy(), -(t - lp).abs().to_numpy()


def test_gator_matches_closed_form():
    df = deterministic_frame(200)
    out = INDICATORS.create("gator").compute(df)
    up, lo = _oracle(df)
    np.testing.assert_allclose(out["gator_upper"].to_numpy(), up, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(out["gator_lower"].to_numpy(), lo, rtol=1e-12, atol=1e-12)


def test_gator_custom_periods_match_closed_form():
    df = deterministic_frame(200, seed=3)
    out = INDICATORS.create("gator", jaw=21, teeth=10, lips=4).compute(df)
    up, lo = _oracle(df, jaw=21, teeth=10, lips=4)
    np.testing.assert_allclose(out["gator_upper"].to_numpy(), up, rtol=1e-12, atol=1e-12)
    np.testing.assert_allclose(out["gator_lower"].to_numpy(), lo, rtol=1e-12, atol=1e-12)


def test_gator_sign_invariants():
    # upper is |.| >= 0, lower is -|.| <= 0, everywhere they are defined.
    out = INDICATORS.create("gator").compute(deterministic_frame(300))
    up = out["gator_upper"].dropna().to_numpy()
    lo = out["gator_lower"].dropna().to_numpy()
    assert up.size > 100 and lo.size > 100
    assert (up >= 0).all()
    assert (lo <= 0).all()
    # a real walk keeps the Alligator's mouth moving, so the bars actually vary
    assert up.std() > 0 and lo.std() > 0


def test_gator_flat_series_both_bars_zero():
    # Constant H/L -> all three SMMA lines equal the constant -> both gaps are exactly 0.
    out = INDICATORS.create("gator").compute(frame([5.0] * 40, high=[5.0] * 40, low=[5.0] * 40))
    defined_up = out["gator_upper"].dropna().to_numpy()
    defined_lo = out["gator_lower"].dropna().to_numpy()
    assert defined_up.size > 0
    np.testing.assert_allclose(defined_up, 0.0, atol=1e-12)
    np.testing.assert_allclose(defined_lo, 0.0, atol=1e-12)


def test_gator_warmup_is_longest_line():
    # First defined value appears only once the longest line (jaw) has filled: idx jaw-1.
    df = deterministic_frame(60)
    out = INDICATORS.create("gator", jaw=13, teeth=8, lips=5).compute(df)
    up = out["gator_upper"]
    assert up.iloc[:12].isna().all()
    assert np.isfinite(up.iloc[12])


def test_gator_short_frame_all_nan():
    out = INDICATORS.create("gator").compute(frame([1.0, 2.0, 3.0]))
    assert out["gator_upper"].isna().all()
    assert out["gator_lower"].isna().all()


def test_gator_output_contract():
    out = INDICATORS.create("gator").compute(deterministic_frame(50))
    assert list(out.columns) == ["gator_upper", "gator_lower"]
    assert len(out) == 50
    assert out["gator_upper"].dtype == np.float64
    assert out["gator_lower"].dtype == np.float64
