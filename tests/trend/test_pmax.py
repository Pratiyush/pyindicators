"""PMAX (Profit Maximizer) — golden / closed-form + edge cases.

PMAX is a Supertrend-style ATR trail around a moving average of close. It is stateful
(path-dependent) and has no simple closed form on a trending series, so we pin the cases
that *are* exact (flat market, warm-up, direction sign in clear trends, structural
invariants) and leave numeric parity to ``tests/parity/test_parity_pmax.py``.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.trend.pmax import pmax  # noqa: F401  (import fires @register for self-verify)
from pyindicators.volatility.atr import atr


def test_pmax_flat_market_parks_on_the_constant():
    # H=L=C=const -> TR 0 -> ATR 0 and MA=const -> both bands collapse onto C, so the line
    # is exactly C once warmed up; with close never below the (collapsed) up band, dir = +1.
    n, c = 30, 7.5
    f = frame([c] * n, high=[c] * n, low=[c] * n)
    out = INDICATORS.create("pmax", length=10, mult=3.0).compute(f)
    assert out["pmax"].iloc[:9].isna().all()  # warm-up = length-1 NaNs
    np.testing.assert_array_equal(out["pmax"].to_numpy()[9:], np.full(n - 9, c))
    assert set(np.unique(out["pmax_dir"].dropna().to_numpy())) <= {1.0}


def test_pmax_short_frame_all_nan():
    out = INDICATORS.create("pmax", length=10).compute(frame([1.0, 2.0, 3.0]))
    assert out["pmax"].isna().all()
    assert out["pmax_dir"].isna().all()


def test_pmax_uptrend_long_below_price():
    # In a steady uptrend the trail sits on the lower band below price and reports +1.
    c = np.arange(1.0, 140.0)
    f = frame(c, high=c + 0.5, low=c - 0.5)
    out = INDICATORS.create("pmax", length=10, mult=3.0).compute(f)
    assert out["pmax_dir"].iloc[-1] == 1.0
    assert out["pmax"].iloc[-1] < c[-1]


def test_pmax_downtrend_short_above_price():
    c = np.arange(140.0, 1.0, -1.0)
    f = frame(c, high=c + 0.5, low=c - 0.5)
    out = INDICATORS.create("pmax", length=10, mult=3.0).compute(f)
    assert out["pmax_dir"].iloc[-1] == -1.0
    assert out["pmax"].iloc[-1] > c[-1]


def test_pmax_finite_exactly_over_atr_support():
    # Both outputs are defined exactly where ATR is (index >= length-1); dir is only emitted
    # where the line is, and only ever takes the values -1 / +1.
    df = deterministic_frame(150)
    out = INDICATORS.create("pmax", length=10, mult=3.0).compute(df)
    a_finite = np.isfinite(atr(df, 10).to_numpy())
    line_finite = np.isfinite(out["pmax"].to_numpy())
    np.testing.assert_array_equal(line_finite, a_finite)
    np.testing.assert_array_equal(np.isfinite(out["pmax_dir"].to_numpy()), line_finite)
    assert set(np.unique(out["pmax_dir"].dropna().to_numpy())) <= {-1.0, 1.0}


def test_pmax_is_causal_prefix_stable():
    # Path-dependent but causal: computing on a prefix matches the same bars of the full run.
    df = deterministic_frame(200)
    full = INDICATORS.create("pmax", length=10, mult=3.0).compute(df)["pmax"].to_numpy()
    pre = INDICATORS.create("pmax", length=10, mult=3.0).compute(df.iloc[:150])["pmax"].to_numpy()
    mask = np.isfinite(full[:150]) & np.isfinite(pre)
    assert mask.sum() > 100
    np.testing.assert_allclose(full[:150][mask], pre[mask], rtol=0, atol=0)


def test_pmax_mult_widens_the_long_gap():
    # A larger ATR multiple sets a looser long stop (further below price) in an uptrend.
    c = np.arange(1.0, 140.0)
    f = frame(c, high=c + 0.5, low=c - 0.5)
    tight = INDICATORS.create("pmax", length=10, mult=1.0).compute(f)["pmax"].iloc[-1]
    loose = INDICATORS.create("pmax", length=10, mult=5.0).compute(f)["pmax"].iloc[-1]
    assert loose < tight < c[-1]


def test_pmax_output_contract():
    out = INDICATORS.create("pmax", length=10).compute(deterministic_frame(60))
    assert list(out.columns) == ["pmax", "pmax_dir"]
    assert len(out) == 60
    assert all(str(out[col].dtype) == "float64" for col in out.columns)
