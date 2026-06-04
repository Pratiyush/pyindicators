"""MAMA — structural / golden + edge cases (TA-Lib MESA Adaptive MA)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.trend.mama import _HT_START, _LOOKBACK, _mama_fama, mama  # noqa: F401 — @register


def test_outputs_are_mama_and_fama():
    df = deterministic_frame()
    out = INDICATORS.create("mama").compute(df)
    assert list(out.columns) == ["mama", "fama"]
    assert out.index.equals(df.index)


def test_lookback_is_nan_then_finite():
    out = INDICATORS.create("mama").compute(deterministic_frame())
    for col in ("mama", "fama"):
        assert out[col].iloc[:_LOOKBACK].isna().all()
        assert out[col].iloc[_LOOKBACK:].notna().all()


def test_short_frame_all_nan():
    # fewer bars than the 32-bar lookback -> every emitted value is NaN
    out = INDICATORS.create("mama").compute(deterministic_frame(20))
    assert out["mama"].isna().all()
    assert out["fama"].isna().all()


def test_empty_series():
    m, f = _mama_fama(pd.Series([], dtype="float64"))
    assert m.empty and f.empty


def test_fama_lags_mama_toward_price_range():
    # both lines stay inside the observed price range (an EMA can't overshoot a bounded walk).
    df = deterministic_frame()
    out = INDICATORS.create("mama").compute(df)
    c = df["close"].to_numpy()
    for col in ("mama", "fama"):
        vals = out[col].dropna().to_numpy()
        assert vals.min() >= c.min() - 1e-9
        assert vals.max() <= c.max() + 1e-9


def test_nan_close_propagates_not_int_crash():
    # a NaN tick must propagate as NaN (period guard), never blow up the adaptive recurrence.
    close = deterministic_frame()["close"].copy()
    close.iloc[200] = np.nan
    m, f = _mama_fama(close)
    assert m.iloc[200:].isna().all()
    assert f.iloc[200:].isna().all()


def test_constant_series_converges_to_constant_on_tail():
    # a flat price has a frozen phase -> the seeded EMAs (prev = 0 at bar 6) climb toward the
    # constant and settle onto it on the tail; both lines stay finite and bounded by it.
    out = INDICATORS.create("mama").compute(frame([50.0] * 200))
    for col in ("mama", "fama"):
        vals = out[col].dropna().to_numpy()
        assert (vals <= 50.0 + 1e-9).all()  # an EMA of a constant never overshoots it
        np.testing.assert_allclose(vals[-50:], 50.0, atol=1e-6)  # settled on the tail


def test_functional_matches_registry():
    df = deterministic_frame()
    reg = INDICATORS.create("mama").compute(df)
    fn = mama(df["close"])
    np.testing.assert_array_equal(fn["mama"].to_numpy(), reg["mama"].to_numpy())
    np.testing.assert_array_equal(fn["fama"].to_numpy(), reg["fama"].to_numpy())
