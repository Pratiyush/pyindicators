"""Structure indicators (rolling high/low, percent-from-high/low) — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS


def test_rolling_high_low_on_ramp():
    c = np.arange(1, 11.0)  # strictly rising
    f = frame(c, high=c, low=c)
    hh = INDICATORS.create("rolling_high", length=3).compute(f)["rolling_high"]
    ll = INDICATORS.create("rolling_low", length=3).compute(f)["rolling_low"]
    np.testing.assert_allclose(hh.iloc[2:], c[2:])  # rising -> max is the current bar
    np.testing.assert_allclose(ll.iloc[2:], c[:8])  # min is 2 bars back


def test_pct_from_high_at_new_high_is_zero():
    c = np.arange(1, 11.0)
    out = INDICATORS.create("pct_from_high", length=3).compute(frame(c, high=c, low=c))["pct_from_high"]
    np.testing.assert_allclose(out.iloc[2:], 0.0)  # close == rolling high


def test_pct_from_low_is_positive_above_low():
    c = np.arange(1, 11.0)
    out = INDICATORS.create("pct_from_low", length=3).compute(frame(c, high=c, low=c))["pct_from_low"]
    assert (out.iloc[2:] > 0).all()


def test_short_frame_all_nan():
    assert INDICATORS.create("rolling_high").compute(frame([1.0, 2.0]))["rolling_high"].isna().all()
