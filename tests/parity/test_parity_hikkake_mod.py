"""Modified Hikkake parity — EXACT integer match vs ``talib.CDLHIKKAKEMOD``.

CDLHIKKAKEMOD is a stateful setup/confirmation pattern whose outputs span ``-200/-100/0/100/200``
(a confirmed breakout adds a second ``±100`` to the setup). The comparison is a bit-exact integer
equality with no tolerance, on the deterministic walk, genuine AAPL daily bars, and a crafted
frame that actually exercises a setup-plus-confirmation (so the ``±200`` path is covered).
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.hikkake_mod import hikkake_mod  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("hikkake_mod").compute(df)["hikkake_mod"].to_numpy()
    ref = talib.CDLHIKKAKEMOD(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)  # candles are integer-exact; no tolerance


def _confirm_frame():
    # 10 flat warm-up bars, then a bullish setup (contracting nest breaking down with the middle
    # bar closing near its low) at bar 13 and its confirmation (close above high[12]) at bar 14.
    o = [100.0] * 15
    h = [110.0] * 10 + [120.0, 118.0, 116.0, 115.0, 118.0]
    low = [90.0] * 10 + [80.0, 82.0, 84.0, 83.0, 100.0]
    c = [100.0] * 10 + [100.0, 81.0, 100.0, 100.0, 117.0]
    return frame(c, high=h, low=low, open_=o)


def test_hikkake_mod_parity_synthetic():
    _check(deterministic_frame())


def test_hikkake_mod_parity_confirmation_frame():
    df = _confirm_frame()
    ref = talib.CDLHIKKAKEMOD(*_ohlc(df)).astype("float64")
    assert np.any(np.abs(ref) == 100)  # the setup fires
    assert np.any(np.abs(ref) == 200)  # ...and is confirmed (the ±200 path)
    _check(df)


def test_hikkake_mod_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDLHIKKAKEMOD(*_ohlc(df)).astype("float64")
    assert np.any(ref != 0)  # the real fixture actually exercises the pattern
    _check(df)
