"""Money-flow indicators: ADL, Chaikin Money Flow, Williams A/D."""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators import INDICATORS


def _frame(close, *, high=None, low=None, volume=1e6):
    close = np.asarray(close, dtype="float64")
    n = len(close)
    ts = pd.date_range("2018-01-01", periods=n, freq="D", tz="UTC")
    high = close * 1.01 if high is None else np.asarray(high, "float64")
    low = close * 0.99 if low is None else np.asarray(low, "float64")
    vol = np.full(n, volume) if np.isscalar(volume) else np.asarray(volume, "float64")
    return pd.DataFrame({"ts": ts, "open": close, "high": high, "low": low, "close": close,
                         "close_raw": close, "volume": vol, "adj_factor": 1.0})


def test_adl_accumulates_when_closing_near_highs():
    # close at the high each bar -> MFM = +1 -> ADL strictly rising.
    n = 20
    close = np.linspace(100, 120, n)
    out = INDICATORS.create("adl").compute(_frame(close, high=close, low=close - 1))
    assert (out["adl"].diff().dropna() > 0).all()


def test_adl_handles_zero_range_bars():
    out = INDICATORS.create("adl").compute(_frame([10.0] * 5, high=[10.0] * 5, low=[10.0] * 5))
    np.testing.assert_allclose(out["adl"].to_numpy(), 0.0)  # H==L -> MFM 0


def test_cmf_bounded_and_positive_on_accumulation():
    n = 40
    close = np.linspace(100, 130, n)
    out = INDICATORS.create("cmf", period=20).compute(_frame(close, high=close, low=close - 1))
    val = out["cmf"].dropna()
    assert (val >= -1.0 - 1e-9).all() and (val <= 1.0 + 1e-9).all()
    assert val.iloc[-1] > 0  # closing at highs = accumulation


def test_cmf_zero_volume_is_nan_not_inf():
    out = INDICATORS.create("cmf", period=5).compute(_frame(np.arange(1.0, 21.0), volume=0.0))
    assert not np.isinf(out["cmf"].to_numpy()).any()
    assert out["cmf"].dropna().empty  # all NaN (no volume)


def test_williams_ad_is_cumulative_and_finite():
    out = INDICATORS.create("williams_ad").compute(_frame(np.linspace(50, 80, 30)))
    assert np.isfinite(out["williams_ad"].iloc[-1])
    assert out["williams_ad"].iloc[0] == 0.0  # first bar has no prior close
