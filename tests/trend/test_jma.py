"""Jurik Moving Average — golden + edge cases."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.trend.jma import jma  # noqa: F401 — import so @register fires before create


def test_jma_flat_series_converges_to_constant():
    # Zero volatility -> the three-stage filter is a steady EMA toward the constant; after the
    # length-1 warm-up the line sits exactly on the flat price.
    out = INDICATORS.create("jma", length=7).compute(frame([42.0] * 60))["jma"]
    np.testing.assert_allclose(out.dropna().to_numpy(), 42.0, atol=1e-9)


def test_jma_warmup_nan_count():
    # pandas-ta zeroes the first length-1 bars to NaN; bar length-1 is the first finite value.
    out = INDICATORS.create("jma", length=7).compute(deterministic_frame(200))["jma"]
    assert out.iloc[:6].isna().all()
    assert out.iloc[6:].notna().all()


def test_jma_short_frame_all_nan():
    # Frame shorter than the warm-up -> every bar is NaN.
    out = INDICATORS.create("jma", length=7).compute(frame([1.0, 2.0, 3.0]))["jma"]
    assert out.isna().all()


def test_jma_empty_series():
    assert jma(pd.Series([], dtype="float64")).empty  # m == 0 guard


def test_jma_finite_and_varies_on_real_trend():
    out = INDICATORS.create("jma", length=7).compute(deterministic_frame(200))["jma"]
    v = out.dropna().to_numpy()
    assert v.size > 100 and v.std() > 0


def test_jma_stays_within_price_range():
    f = deterministic_frame(200)
    out = INDICATORS.create("jma", length=7).compute(f)["jma"]
    v = out.dropna().to_numpy()
    c = f["close"].to_numpy()
    # A smoother of price cannot leave the observed price envelope by more than tiny overshoot.
    assert v.min() >= c.min() - 1.0 and v.max() <= c.max() + 1.0


def test_jma_length_one_is_passthrough_tail():
    # length=1 -> beta 0, alpha 1 at the steady state: the filter tracks price closely on a
    # smooth ramp (no warm-up NaN since length-1 == 0).
    out = INDICATORS.create("jma", length=1).compute(frame(np.arange(1.0, 40.0)))["jma"]
    assert out.notna().all()


def test_jma_phase_changes_output():
    f = deterministic_frame(200)
    neg = INDICATORS.create("jma", length=7, phase=-100.0).compute(f)["jma"].dropna()
    pos = INDICATORS.create("jma", length=7, phase=100.0).compute(f)["jma"].dropna()
    assert not np.allclose(neg.to_numpy(), pos.to_numpy())  # phase ratio actually bites


def test_jma_rejects_out_of_range_phase():
    with pytest.raises(Exception):  # noqa: B017 — pydantic ValidationError on phase > 100
        INDICATORS.create("jma", phase=200.0)


def test_phase_ratio_clamps():
    # the helper guards |phase|>100 even though Params already constrains the public range
    from pyindicators.trend.jma import _phase_ratio

    assert _phase_ratio(-200.0) == 0.5
    assert _phase_ratio(200.0) == 2.5
    assert _phase_ratio(0.0) == 1.5
