"""Ichimoku Kinko Hyo — golden / closed-form, warm-up, no-shift causality, edge cases."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.trend.ichimoku import ichimoku  # noqa: F401  (fires @register for create())


def _create(**kw):
    return INDICATORS.create("ichimoku", **kw)


def test_closed_form_on_unit_ramp():
    # On a unit-slope ramp with high=close+0.5, low=close-0.5, the n-bar midprice at bar i is
    # 0.5*((c_i+0.5)+(c_{i-n+1}-0.5)) = (c_i + c_{i-n+1})/2 = c_i - (n-1)/2 (since c steps by 1).
    close = np.arange(0.0, 80.0)
    df = frame(close, high=close + 0.5, low=close - 0.5)
    out = _create(tenkan=9, kijun=26, senkou=52).compute(df)
    idx = np.arange(close.size, dtype="float64")
    exp_tenkan = idx - (9 - 1) / 2.0
    exp_kijun = idx - (26 - 1) / 2.0
    exp_span_b = idx - (52 - 1) / 2.0
    exp_span_a = 0.5 * (exp_tenkan + exp_kijun)
    for col, exp, warm in [
        ("tenkan", exp_tenkan, 9),
        ("kijun", exp_kijun, 26),
        ("span_a", exp_span_a, 26),  # span_a inherits the longer (kijun) warm-up
        ("span_b", exp_span_b, 52),
    ]:
        got = out[col].to_numpy()
        assert np.isnan(got[: warm - 1]).all(), f"{col} should be NaN before warm-up"
        np.testing.assert_allclose(got[warm - 1 :], exp[warm - 1 :], atol=1e-9)


def test_span_a_is_mean_of_tenkan_and_kijun():
    df = deterministic_frame(200)
    out = _create().compute(df)
    np.testing.assert_allclose(
        out["span_a"].to_numpy(),
        0.5 * (out["tenkan"].to_numpy() + out["kijun"].to_numpy()),
        equal_nan=True,
    )


def test_lines_bracketed_by_rolling_extremes():
    # Each midprice line must sit within [lowest low, highest high] of its own window.
    df = deterministic_frame(300)
    out = _create(tenkan=9, kijun=26, senkou=52).compute(df)
    for col, n in [("tenkan", 9), ("kijun", 26), ("span_b", 52)]:
        hi = df["high"].rolling(n, min_periods=n).max().to_numpy()
        lo = df["low"].rolling(n, min_periods=n).min().to_numpy()
        v = out[col].to_numpy()
        m = np.isfinite(v)
        assert (v[m] <= hi[m] + 1e-9).all() and (v[m] >= lo[m] - 1e-9).all()


def test_warmup_matches_window_lengths():
    df = deterministic_frame(120)
    out = _create(tenkan=9, kijun=26, senkou=52).compute(df)
    assert out["tenkan"].first_valid_index() == 8
    assert out["kijun"].first_valid_index() == 25
    assert out["span_a"].first_valid_index() == 25  # gated by the longer of tenkan/kijun
    assert out["span_b"].first_valid_index() == 51


def test_spans_are_not_forward_shifted_no_lookahead():
    # The visual cloud leads price by `kijun` bars (look-ahead); we emit the UNSHIFTED line.
    # Operationalised as truncation invariance: appending future bars can't change past values.
    df = deterministic_frame(200)
    full = _create().compute(df)
    head = _create().compute(df.iloc[:130].copy())
    pd.testing.assert_frame_equal(full.iloc[:130], head, check_exact=False, atol=1e-12)


def test_flat_series_yields_constant_lines_no_nan_from_division():
    # A constant H/L window still has a well-defined midprice (no guarded division here).
    df = frame(np.full(80, 50.0), high=np.full(80, 51.0), low=np.full(80, 49.0))
    out = _create().compute(df)
    finite = out.dropna()
    assert len(finite) > 0
    for col in ("tenkan", "kijun", "span_a", "span_b"):
        np.testing.assert_allclose(finite[col].to_numpy(), 50.0)


def test_short_frame_all_nan():
    df = frame([1.0, 2.0, 3.0], high=[1.5, 2.5, 3.5], low=[0.5, 1.5, 2.5])
    out = _create().compute(df)
    assert out.isna().all().all()


def test_output_contract():
    df = deterministic_frame(90)
    out = _create().compute(df)
    assert list(out.columns) == ["tenkan", "kijun", "span_a", "span_b"]
    assert (out.dtypes == np.float64).all()
    assert len(out) == len(df)
    assert isinstance(out, pd.DataFrame)
