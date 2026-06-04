"""Williams Alligator — golden/closed-form + edge cases.

The three lines are SMMA (== ``base.rma``) of the median price, unshifted. Golden checks
assert each output equals the closed-form ``rma(hl2, length)`` directly, then cover warm-up,
the flat high==low collapse, short frames, ordering, and causality (no forward offset).
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.base import rma
from pyindicators.momentum.alligator import alligator  # noqa: F401  (import fires @register)


def _median(df):
    return (df["high"] + df["low"]) / 2.0


def test_alligator_equals_rma_of_median():
    # Closed-form: each line is exactly Wilder's RMA of the median price at its own length.
    df = deterministic_frame(200)
    out = INDICATORS.create("alligator", jaw=13, teeth=8, lips=5).compute(df)
    med = _median(df)
    for col, length in (("alligator_jaw", 13), ("alligator_teeth", 8), ("alligator_lips", 5)):
        np.testing.assert_allclose(
            out[col].to_numpy(), rma(med, length).to_numpy(), equal_nan=True, rtol=1e-12
        )


def test_alligator_columns_and_dtype():
    out = INDICATORS.create("alligator").compute(deterministic_frame(60))
    assert list(out.columns) == ["alligator_jaw", "alligator_teeth", "alligator_lips"]
    assert all(str(out[c].dtype) == "float64" for c in out.columns)
    assert len(out) == 60  # output length == input length


def test_alligator_warmup_first_valid_index():
    # RMA's first valid output is at index length-1 (SMA seed); lips warms up before jaw.
    out = INDICATORS.create("alligator", jaw=13, teeth=8, lips=5).compute(deterministic_frame(40))
    assert out["alligator_lips"].iloc[:4].isna().all() and not np.isnan(out["alligator_lips"].iloc[4])
    assert out["alligator_teeth"].iloc[:7].isna().all() and not np.isnan(out["alligator_teeth"].iloc[7])
    assert out["alligator_jaw"].iloc[:12].isna().all() and not np.isnan(out["alligator_jaw"].iloc[12])


def test_alligator_flat_high_low_collapses_to_constant():
    # high == low every bar -> median is constant -> all three SMMAs equal that constant.
    flat = np.full(40, 5.0)
    out = INDICATORS.create("alligator").compute(frame(flat, high=flat, low=flat))
    for col in out.columns:
        np.testing.assert_allclose(out[col].dropna().to_numpy(), 5.0)


def test_alligator_constant_after_warmup_lines_converge():
    # On a constant median all three lines settle to the same value once warmed up.
    n = 80
    df = frame(np.full(n, 10.0), high=np.full(n, 11.0), low=np.full(n, 9.0))  # median == 10
    out = INDICATORS.create("alligator").compute(df)
    last = out.iloc[-1]
    np.testing.assert_allclose(last.to_numpy(), 10.0)


def test_alligator_short_frame_all_nan():
    # Fewer rows than the slowest (jaw) period -> jaw all NaN; shorter than lips -> all NaN.
    out = INDICATORS.create("alligator", jaw=13, teeth=8, lips=5).compute(frame([1.0, 2.0, 3.0]))
    assert out["alligator_jaw"].isna().all()
    assert out["alligator_teeth"].isna().all()
    assert out["alligator_lips"].isna().all()


def test_alligator_causal_no_forward_shift():
    # Causal: truncating future bars must not change any already-emitted value (no look-ahead).
    df = deterministic_frame(120)
    full = INDICATORS.create("alligator").compute(df)
    cut = INDICATORS.create("alligator").compute(df.iloc[:90])
    np.testing.assert_allclose(
        full.iloc[:90].to_numpy(), cut.to_numpy(), equal_nan=True, rtol=1e-12
    )


def test_alligator_lips_tracks_median_faster_than_jaw():
    # Fastest line (lips) hugs the median more tightly than the slowest (jaw) in a trend.
    rng = np.arange(1.0, 120.0)
    df = frame(rng, high=rng + 0.5, low=rng - 0.5)  # steady uptrend, median == rng
    out = INDICATORS.create("alligator").compute(df)
    med = _median(df)
    tail = slice(-20, None)
    lips_gap = (med.iloc[tail] - out["alligator_lips"].iloc[tail]).abs().mean()
    jaw_gap = (med.iloc[tail] - out["alligator_jaw"].iloc[tail]).abs().mean()
    assert lips_gap < jaw_gap


def test_alligator_rejects_unordered_periods():
    # jaw > teeth > lips is required; an out-of-order config must be rejected by Params.
    import pytest

    with pytest.raises(ValueError):
        INDICATORS.create("alligator", jaw=5, teeth=8, lips=13)


def test_alligator_rejects_unknown_param():
    import pytest

    with pytest.raises(ValueError):
        INDICATORS.create("alligator", offset=3)
