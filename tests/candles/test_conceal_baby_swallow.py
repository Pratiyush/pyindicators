"""Concealing Baby Swallow — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.conceal_baby_swallow import (  # noqa: F401  (import fires @register)
    conceal_baby_swallow,
)

# 13 short black warm-up bars (body ~0.5, tiny shadows) so the ShadowVeryShort average is small
# and stable by the time the four-candle pattern forms at bars 13..16.
_WARM = 13
_WO = [50.0] * _WARM
_WC = [49.5] * _WARM
_WH = [50.1] * _WARM
_WL = [49.4] * _WARM

# A hand-built Concealing Baby Swallow (verified to score +100 against talib.CDLCONCEALBABYSWALL):
# 1st & 2nd black marubozu, 3rd black with a long upper shadow gapping down into the 2nd body,
# 4th black engulfing the 3rd's range. Pattern completes on bar 16.
_PO = [48.0, 43.5, 39.0, 41.5]
_PC = [44.0, 40.0, 37.5, 36.0]
_PH = [48.02, 43.52, 41.0, 41.5]
_PL = [43.98, 39.98, 37.4, 37.0]


def _cbs(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("conceal_baby_swallow").compute(df)["conceal_baby_swallow"].to_numpy()


def _full():
    return (_WO + _PO, _WH + _PH, _WL + _PL, _WC + _PC)


def test_conceal_baby_swallow_golden_hit():
    o, h, low, c = _full()
    assert _cbs(o, h, low, c)[16] == 100.0


def test_conceal_baby_swallow_is_bullish_only():
    # Pattern is purely bullish: nowhere should it emit a negative value.
    o, h, low, c = _full()
    out = _cbs(o, h, low, c)
    assert out.min() >= 0.0
    assert set(np.unique(out)) <= {0.0, 100.0}


def test_conceal_baby_swallow_white_fourth_breaks_it():
    # Flip the 4th candle to white -> no pattern (all four candles must be black).
    o, h, low, c = _full()
    o = list(o)
    c = list(c)
    o[16], c[16] = c[16], o[16]  # swap open/close -> white
    assert _cbs(o, h, low, c)[16] == 0.0


def test_conceal_baby_swallow_no_engulf_breaks_it():
    # 4th candle no longer engulfs the 3rd (high ties the 3rd high -> strict test fails).
    o, h, low, c = _full()
    h = list(h)
    h[16] = _PH[2]  # == 3rd-candle high
    assert _cbs(o, h, low, c)[16] == 0.0


def test_conceal_baby_swallow_warmup_is_zero():
    o, h, low, c = _full()
    np.testing.assert_array_equal(_cbs(o, h, low, c)[:13], 0.0)  # TA-Lib lookback = 13


def test_conceal_baby_swallow_constant_frame_is_zero():
    # A flat doji-only frame (open == close, no range) can never form the pattern.
    flat = [100.0] * 40
    out = INDICATORS.create("conceal_baby_swallow").compute(frame(flat))["conceal_baby_swallow"]
    np.testing.assert_array_equal(out.to_numpy(), 0.0)


def test_conceal_baby_swallow_short_frame_is_zero():
    # Frames shorter than the lookback yield all zeros (no warm-up satisfied).
    for n in (1, 4, 10, 13):
        close = np.linspace(100.0, 110.0, n)
        out = INDICATORS.create("conceal_baby_swallow").compute(frame(close))
        np.testing.assert_array_equal(out["conceal_baby_swallow"].to_numpy(), 0.0)


def test_conceal_baby_swallow_output_contract():
    o, h, low, c = _full()
    out = INDICATORS.create("conceal_baby_swallow").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["conceal_baby_swallow"]
    assert set(np.unique(out["conceal_baby_swallow"].to_numpy())) <= {
        -100.0,
        -80.0,
        0.0,
        80.0,
        100.0,
    }
