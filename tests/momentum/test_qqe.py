"""QQE — Quantitative Qualitative Estimation: golden + edge cases + structural invariants."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.momentum.qqe import qqe  # noqa: F401  (import fires @INDICATORS.register)


def test_qqe_columns_and_dtype():
    out = INDICATORS.create("qqe").compute(deterministic_frame(200))
    assert list(out.columns) == ["qqe", "qqe_rsima", "qqe_long", "qqe_short"]
    assert all(str(d) == "float64" for d in out.dtypes)
    assert len(out) == 200  # output length == input length


def test_qqe_rsima_bounded_0_100():
    # The basis is an EMA of RSI, so it must stay within RSI's [0, 100] envelope.
    v = INDICATORS.create("qqe").compute(deterministic_frame(300))["qqe_rsima"].dropna().to_numpy()
    assert v.size > 0
    assert v.min() >= -1e-9 and v.max() <= 100.0 + 1e-9


def test_qqe_long_short_mutually_exclusive():
    # On any bar exactly one trend is active, so the sparse long/short lines never overlap.
    out = INDICATORS.create("qqe").compute(deterministic_frame(300))
    long_finite = np.isfinite(out["qqe_long"].to_numpy())
    short_finite = np.isfinite(out["qqe_short"].to_numpy())
    assert not np.any(long_finite & short_finite)


def test_qqe_active_line_equals_active_trend_line():
    # ``qqe`` carries whichever of the long/short lines is active that bar.
    out = INDICATORS.create("qqe").compute(deterministic_frame(300))
    q = out["qqe"].to_numpy()
    long_a = out["qqe_long"].to_numpy()
    short_a = out["qqe_short"].to_numpy()
    combined = np.where(np.isfinite(long_a), long_a, short_a)
    warm = np.isfinite(q)
    np.testing.assert_allclose(q[warm], combined[warm], rtol=0, atol=0)


def test_qqe_finite_and_varies_on_real_trend():
    out = INDICATORS.create("qqe").compute(deterministic_frame(300))["qqe"]
    v = out.dropna().to_numpy()
    assert v.size > 100 and v.std() > 0  # the trailing line actually moves


def test_qqe_golden_anchor():
    # Pinned last-bar values on the fixed 400-bar deterministic frame (warmed tail): at the
    # final bar the trend is short, so ``qqe`` == ``qqe_short`` and ``qqe_long`` is NaN.
    out = INDICATORS.create("qqe").compute(deterministic_frame())
    assert np.isclose(out["qqe"].iloc[-1], 47.26361034622805, rtol=0, atol=1e-9)
    assert np.isclose(out["qqe_rsima"].iloc[-1], 40.497680028708174, rtol=0, atol=1e-9)
    assert np.isclose(out["qqe_short"].iloc[-1], 47.26361034622805, rtol=0, atol=1e-9)
    assert np.isnan(out["qqe_long"].iloc[-1])


def test_qqe_short_frame_active_line_all_nan():
    # Far fewer bars than the warm-up (RSI 14 + EMA 5 + two EMA-27 stages) -> nothing warms.
    out = INDICATORS.create("qqe").compute(frame([float(x) for x in range(1, 12)]))
    assert out["qqe_rsima"].isna().all()
    # ``qqe`` is seeded at bar 0 from the (NaN) smoothed RSI, so the whole line stays NaN here.
    assert out["qqe"].isna().all()
