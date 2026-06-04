"""Three Black Crows parity — EXACT integer match vs ``talib.CDL3BLACKCROWS``.

Checked on the synthetic walk and on genuine AAPL daily bars (no tolerance — candles are
integer-exact). A hand-built four-bar frame additionally pins a real -100 emission, so parity
is verified on an actual pattern hit and not only on the all-zero fixtures.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.three_black_crows import (
    three_black_crows,  # noqa: F401  (fires @register)
)

talib = pytest.importorskip("talib")

_LOOKBACK = 13


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("three_black_crows").compute(df)["three_black_crows"].to_numpy()
    ref = talib.CDL3BLACKCROWS(*_ohlc(df)).astype("float64")
    ref[:_LOOKBACK] = 0.0  # force the lookback warm-up to 0 to match talib's outBegIdx offset
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def _hit_frame():
    # 10 warm-up bars (HL range 4.0 -> ShadowVeryShort avg ~0.4) then four bars forming the
    # pattern: a white candle, then three declining black crows with tiny lower shadows, each
    # opening inside the prior body. talib emits -100 at the final bar.
    warm = 10
    o = [100.0] * warm + [100.0, 109.0, 108.0, 106.0]
    c = [101.0] * warm + [110.5, 106.0, 104.0, 102.0]
    h = [103.0] * warm + [110.7, 109.1, 108.1, 106.1]
    low = [99.0] * warm + [99.5, 105.9, 103.9, 101.9]
    return frame(c, high=h, low=low, open_=o)


def test_three_black_crows_parity_synthetic():
    _check(deterministic_frame())


def test_three_black_crows_parity_real():
    _check(real_frame())  # genuine AAPL daily bars


def test_three_black_crows_parity_constructed_hit():
    df = _hit_frame()
    ref = talib.CDL3BLACKCROWS(*_ohlc(df)).astype("float64")
    assert np.any(ref == -100)  # the constructed frame actually triggers the pattern
    _check(df)
