"""Gravestone Doji — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.gravestone_doji import gravestone_doji  # noqa: F401  (fires @register)

# 10 warm-up bars wide enough that the BodyDoji / ShadowVeryShort averages (10% of the average
# high-low range) are well defined by the time the pattern forms at bar 10.
_WARM = 10
_WO = [100.0] * _WARM
_WC = [100.5] * _WARM
_WH = [101.0] * _WARM
_WL = [99.5] * _WARM


def _grave(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("gravestone_doji").compute(df)["gravestone_doji"].to_numpy()


def test_gravestone_doji_hit():
    # Doji body at the bottom: open == close == low, long upper shadow -> +100.
    o = _WO + [100.0]
    c = _WC + [100.0]
    h = _WH + [101.5]
    low = _WL + [100.0]
    assert _grave(o, h, low, c)[10] == 100.0


def test_gravestone_doji_no_lower_shadow_required():
    # A meaningful lower shadow disqualifies the gravestone (body must sit at the low).
    o = _WO + [100.0]
    c = _WC + [100.0]
    h = _WH + [101.5]
    low = _WL + [98.0]  # large lower shadow
    assert _grave(o, h, low, c)[10] == 0.0


def test_gravestone_doji_needs_upper_shadow():
    # A doji with no upper shadow (body at the top) is not a gravestone.
    o = _WO + [100.0]
    c = _WC + [100.0]
    h = _WH + [100.0]  # no upper shadow
    low = _WL + [98.5]
    assert _grave(o, h, low, c)[10] == 0.0


def test_gravestone_doji_big_body_is_not_doji():
    # A large real body is not a doji even with a long upper shadow -> 0.
    o = _WO + [100.0]
    c = _WC + [103.0]  # big body
    h = _WH + [106.0]
    low = _WL + [100.0]
    assert _grave(o, h, low, c)[10] == 0.0


def test_gravestone_doji_constant_frame_is_zero():
    # A flat frame (range 0 everywhere) has no shadows -> never a gravestone.
    flat = [50.0] * 30
    out = _grave(flat, flat, flat, flat)
    np.testing.assert_array_equal(out, 0.0)


def test_gravestone_doji_short_frame_is_zero():
    # Fewer bars than the lookback -> all zeros (averages undefined).
    o = [100.0, 100.0, 100.0]
    c = [100.0, 100.0, 100.0]
    h = [101.0, 101.0, 101.5]
    low = [100.0, 100.0, 100.0]
    np.testing.assert_array_equal(_grave(o, h, low, c), 0.0)


def test_gravestone_doji_warmup_is_zero():
    o = _WO + [100.0]
    c = _WC + [100.0]
    h = _WH + [101.5]
    low = _WL + [100.0]
    np.testing.assert_array_equal(_grave(o, h, low, c)[:10], 0.0)  # TA-Lib lookback = 10


def test_gravestone_doji_output_contract():
    o = _WO + [100.0]
    c = _WC + [100.0]
    h = _WH + [101.5]
    low = _WL + [100.0]
    out = INDICATORS.create("gravestone_doji").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["gravestone_doji"]
    assert set(np.unique(out["gravestone_doji"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
