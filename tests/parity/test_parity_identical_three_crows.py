"""Identical Three Crows parity — EXACT integer match vs ``talib.CDLIDENTICAL3CROWS``.

Checked on the synthetic walk and on genuine AAPL daily bars (no tolerance — candles are
integer-exact). A hand-built three-bar frame additionally pins a real -100 emission, so parity
is verified on an actual pattern hit (including the inclusive ``Equal`` open band) and not only
on the all-zero fixtures.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.identical_three_crows import (
    identical_three_crows,  # noqa: F401  (fires @register)
)

talib = pytest.importorskip("talib")

_LOOKBACK = 12


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = (
        INDICATORS.create("identical_three_crows")
        .compute(df)["identical_three_crows"]
        .to_numpy()
    )
    ref = talib.CDLIDENTICAL3CROWS(*_ohlc(df)).astype("float64")
    ref[:_LOOKBACK] = 0.0  # force the lookback warm-up to 0 to match talib's outBegIdx offset
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def _hit_frame():
    # 12 warm-up bars (HL range 4.0 -> ShadowVeryShort avg ~0.4, Equal band ~0.2) then three
    # identical black crows: declining closes, tiny lower shadows, each opening exactly at the
    # prior crow's close (the inclusive boundary of the Equal band). talib emits -100 at i=14.
    warm = 12
    o = [100.0] * warm + [110.0, 108.0, 106.0]
    c = [101.0] * warm + [108.0, 106.0, 104.0]
    h = [103.0] * warm + [110.1, 108.1, 106.1]
    low = [99.0] * warm + [107.99, 105.99, 103.99]
    return frame(c, high=h, low=low, open_=o)


def test_identical_three_crows_parity_synthetic():
    _check(deterministic_frame())


def test_identical_three_crows_parity_real():
    _check(real_frame())  # genuine AAPL daily bars


def test_identical_three_crows_parity_constructed_hit():
    df = _hit_frame()
    ref = talib.CDLIDENTICAL3CROWS(*_ohlc(df)).astype("float64")
    assert np.any(ref == -100)  # the constructed frame actually triggers the pattern
    _check(df)
