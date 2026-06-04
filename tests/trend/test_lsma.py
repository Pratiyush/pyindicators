"""LSMA (Least Squares MA) — golden / closed-form + edge cases.

LSMA is the rolling linear-regression endpoint, so it reproduces any straight line exactly
and passes a constant series through unchanged.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.statistics.linreg import linreg  # noqa: F401  (parity oracle)
from pyindicators.trend.lsma import lsma  # noqa: F401  (import fires @register for create())


def test_lsma_reproduces_a_straight_line_exactly():
    # On y = 3 + 2x the least-squares fit is the line itself, so its endpoint == close.
    x = np.arange(60.0)
    f = frame(3.0 + 2.0 * x)
    out = INDICATORS.create("lsma", length=14).compute(f)["lsma"]
    np.testing.assert_allclose(out.to_numpy()[13:], (3.0 + 2.0 * x)[13:], atol=1e-7)


def test_lsma_constant_series_is_constant():
    out = INDICATORS.create("lsma", length=14).compute(frame([7.0] * 40))["lsma"]
    np.testing.assert_allclose(out.dropna().to_numpy(), 7.0, atol=1e-9)


def test_lsma_warmup_and_first_value():
    # First length-1 bars are NaN; the first defined value appears at index length-1.
    out = INDICATORS.create("lsma", length=14).compute(deterministic_frame(60))["lsma"]
    assert out.iloc[:13].isna().all()
    assert np.isfinite(out.iloc[13])


def test_lsma_short_frame_all_nan():
    out = INDICATORS.create("lsma", length=14).compute(frame([1.0, 2.0, 3.0]))["lsma"]
    assert out.isna().all()


def test_lsma_equals_statistics_linreg():
    # LSMA *is* the linear-regression value — verify the compose matches statistics.linreg.
    df = deterministic_frame(200)
    ours = INDICATORS.create("lsma", length=20).compute(df)["lsma"].to_numpy()
    ref = INDICATORS.create("linreg", length=20).compute(df)["linreg"].to_numpy()
    np.testing.assert_allclose(ours, ref, rtol=1e-12, atol=1e-12, equal_nan=True)
