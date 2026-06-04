"""Chande Kroll Stop — golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.trend.cksp import cksp  # noqa: F401  (import fires @register)
from pyindicators.volatility.atr import atr


def test_cksp_constant_series_sits_on_price():
    # H=L=C=const -> TR 0 -> ATR 0 -> long = max_q(HH - 0) = c, short = min_q(LL + 0) = c.
    c = 50.0
    out = INDICATORS.create("cksp", p=10, x=1.0, q=9).compute(frame([c] * 40))
    lng = out["cksp_long"].dropna().to_numpy()
    sht = out["cksp_short"].dropna().to_numpy()
    assert lng.size > 0 and sht.size > 0
    np.testing.assert_allclose(lng, c, atol=1e-9)
    np.testing.assert_allclose(sht, c, atol=1e-9)


def test_cksp_linear_ramp_first_difference_is_unit():
    # H=L=C=i (a unit ramp). HH(p) and LL(p) both rise by exactly 1/bar, and the RMA-ATR
    # asymptotes to a flat 1.0 (alpha=1/p EMA of a constant TR=1). So once warm, BOTH stops
    # advance by exactly +1.0 per bar — a seed-independent closed form (the tiny residual is
    # the decaying ATR seed transient, gone deep in the tail).
    n = 250
    out = INDICATORS.create("cksp", p=10, x=1.0, q=9).compute(frame(np.arange(float(n))))
    dl = np.diff(out["cksp_long"].to_numpy())
    ds = np.diff(out["cksp_short"].to_numpy())
    np.testing.assert_allclose(dl[-100:], 1.0, atol=1e-7)
    np.testing.assert_allclose(ds[-100:], 1.0, atol=1e-7)


def test_cksp_matches_explicit_atr_composition():
    # Pin the wiring (non-circular vs the closed-form tests above): cksp must equal the
    # documented construction over HH/LL and the SAME ATR our library exposes publicly.
    df = deterministic_frame(300)
    p, x, q = 10, 1.0, 9
    out = INDICATORS.create("cksp", p=p, x=x, q=q).compute(df)
    a = atr(df, p)
    exp_long = (df["high"].rolling(p, min_periods=p).max() - x * a).rolling(q, min_periods=q).max()
    exp_short = (df["low"].rolling(p, min_periods=p).min() + x * a).rolling(q, min_periods=q).min()
    np.testing.assert_allclose(out["cksp_long"].to_numpy(), exp_long.to_numpy(), equal_nan=True)
    np.testing.assert_allclose(out["cksp_short"].to_numpy(), exp_short.to_numpy(), equal_nan=True)


def test_cksp_short_frame_all_nan():
    # Fewer bars than the p+q-1 warm-up -> every output is NaN (nothing fabricated).
    out = INDICATORS.create("cksp", p=10, x=1.0, q=9).compute(frame([1.0, 2.0, 3.0, 4.0]))
    assert out["cksp_long"].isna().all()
    assert out["cksp_short"].isna().all()


def test_cksp_outputs_bracket_extremes_on_real_walk():
    # Long stop is built from HH minus a positive band -> must stay <= rolling-max High.
    # Short stop is LL plus a positive band -> must stay >= rolling-min Low.
    df = deterministic_frame(300)
    p, x, q = 10, 1.0, 9
    out = INDICATORS.create("cksp", p=p, x=x, q=q).compute(df)
    lng = out["cksp_long"]
    sht = out["cksp_short"]
    hh = df["high"].rolling(p, min_periods=p).max().rolling(q, min_periods=q).max()
    ll = df["low"].rolling(p, min_periods=p).min().rolling(q, min_periods=q).min()
    m = lng.notna() & sht.notna()
    assert m.sum() > 100
    # x*ATR > 0 on a non-flat walk, so the inequalities are strict at finite values.
    assert (lng[m] <= hh[m] + 1e-9).all()
    assert (sht[m] >= ll[m] - 1e-9).all()
    assert (lng[m] < hh[m]).all()
    assert (sht[m] > ll[m]).all()


def test_cksp_length_and_columns():
    df = deterministic_frame(120)
    out = INDICATORS.create("cksp").compute(df)
    assert list(out.columns) == ["cksp_long", "cksp_short"]
    assert len(out) == len(df)
    assert out.dtypes.eq(np.float64).all()


def test_cksp_book_mode_differs_from_tv_mode():
    # tvmode swaps the ATR smoother (RMA vs SMA); on a real walk the stops must differ.
    df = deterministic_frame(200)
    tv = INDICATORS.create("cksp", tvmode=True).compute(df)["cksp_long"]
    book = INDICATORS.create("cksp", tvmode=False).compute(df)["cksp_long"]
    m = tv.notna() & book.notna()
    assert m.sum() > 50
    assert not np.allclose(tv[m].to_numpy(), book[m].to_numpy())
