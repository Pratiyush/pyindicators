"""Modified Hikkake — golden + edge cases (deterministic; no reference library).

CDLHIKKAKEMOD is stateful: a three-bar contracting nest (each bar inside the prior) whose
middle bar closes at its extreme is a *setup* (``±100``), and a breakout within three bars is a
*confirmation* (``±200`` — the setup's ``±100`` plus a second ``±100``). Outputs therefore span
``{-200, -100, 0, 100, 200}``. TA-Lib's lookback is 10 (the first 10 bars are 0).
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.hikkake_mod import hikkake_mod  # noqa: F401  (import fires @register)

# 10 flat warm-up bars so the pattern can first form right at the lookback boundary.
_WO = [100.0] * 10
_WC = [100.0] * 10
_WH = [110.0] * 10
_WL = [90.0] * 10


def _hkm(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("hikkake_mod").compute(df)["hikkake_mod"].to_numpy()


def test_hikkake_mod_bullish_setup_then_confirm():
    # Contracting nest (idx10>idx11>idx12), idx13 breaks DOWN (lower high AND lower low) with the
    # middle bar idx11 closing near its low -> bullish setup +100 at idx13; idx14 closes above
    # high[idx12] within 3 bars -> confirmation +200.
    o = [*_WO, 100.0, 100.0, 100.0, 100.0, 100.0]
    h = [*_WH, 120.0, 118.0, 116.0, 115.0, 118.0]
    low = [*_WL, 80.0, 82.0, 84.0, 83.0, 100.0]
    c = [*_WC, 100.0, 81.0, 100.0, 100.0, 117.0]
    out = _hkm(o, h, low, c)
    assert out[13] == 100.0
    assert out[14] == 200.0


def test_hikkake_mod_bearish_setup_then_confirm():
    # Mirror: idx13 breaks UP (higher high AND higher low) with the middle bar idx11 closing near
    # its high -> bearish setup -100; idx14 closes below low[idx12] -> confirmation -200.
    o = [*_WO, 100.0, 100.0, 100.0, 100.0, 100.0]
    h = [*_WH, 120.0, 118.0, 116.0, 117.0, 100.0]
    low = [*_WL, 80.0, 82.0, 84.0, 85.0, 82.0]
    c = [*_WC, 100.0, 117.0, 100.0, 100.0, 83.0]
    out = _hkm(o, h, low, c)
    assert out[13] == -100.0
    assert out[14] == -200.0


def test_hikkake_mod_setup_without_confirmation_stays_100():
    # Same bullish setup at idx13, but idx14 does NOT break out (close stays inside) -> only the
    # setup fires; no confirmation.
    o = [*_WO, 100.0, 100.0, 100.0, 100.0, 100.0]
    h = [*_WH, 120.0, 118.0, 116.0, 115.0, 114.0]
    low = [*_WL, 80.0, 82.0, 84.0, 83.0, 82.0]
    c = [*_WC, 100.0, 81.0, 100.0, 100.0, 100.0]
    out = _hkm(o, h, low, c)
    assert out[13] == 100.0
    assert out[14] == 0.0


def test_hikkake_mod_warmup_is_zero():
    o = [*_WO, 100.0, 100.0, 100.0, 100.0, 100.0]
    h = [*_WH, 120.0, 118.0, 116.0, 115.0, 118.0]
    low = [*_WL, 80.0, 82.0, 84.0, 83.0, 100.0]
    c = [*_WC, 100.0, 81.0, 100.0, 100.0, 117.0]
    np.testing.assert_array_equal(_hkm(o, h, low, c)[:10], 0.0)  # TA-Lib lookback = 10


def test_hikkake_mod_constant_frame_is_zero():
    flat = [100.0] * 40
    np.testing.assert_array_equal(_hkm(flat, flat, flat, flat), 0.0)


def test_hikkake_mod_short_frame_is_zero():
    # Fewer than the 10-bar lookback -> all zero regardless of shape.
    o = [100.0, 101.0, 99.0, 100.0, 102.0]
    h = [105.0, 104.0, 103.0, 102.0, 106.0]
    low = [95.0, 96.0, 97.0, 98.0, 94.0]
    c = [101.0, 100.0, 98.0, 101.0, 103.0]
    np.testing.assert_array_equal(_hkm(o, h, low, c), 0.0)


def test_hikkake_mod_output_contract():
    o = [*_WO, 100.0, 100.0, 100.0, 100.0, 100.0]
    h = [*_WH, 120.0, 118.0, 116.0, 115.0, 118.0]
    low = [*_WL, 80.0, 82.0, 84.0, 83.0, 100.0]
    c = [*_WC, 100.0, 81.0, 100.0, 100.0, 117.0]
    out = INDICATORS.create("hikkake_mod").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["hikkake_mod"]
    assert set(np.unique(out["hikkake_mod"].to_numpy())) <= {-200.0, -100.0, 0.0, 100.0, 200.0}
