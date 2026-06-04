"""Long Line — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.long_line import long_line  # noqa: F401  (import fires @register)

# 10 warm-up bars (body ~0.5, range ~0.7) so by bar 10 the BodyLong average is ~0.5 and the
# ShadowShort average (Shadows/10/1.0 -> half the average of upper+lower) is ~0.1. Then a long
# white candle (body 2.0, tiny shadows), then a long black candle.
_OPEN = [100.0] * 10 + [100.0, 102.0]
_CLOSE = [100.5] * 10 + [102.0, 100.0]
_HIGH = [100.6] * 10 + [102.05, 102.05]
_LOW = [99.9] * 10 + [99.95, 99.95]


def _ll(df):
    return INDICATORS.create("long_line").compute(df)["long_line"].to_numpy()


def test_long_line_white_and_black():
    out = _ll(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    assert out[10] == 100.0  # long white body, both shadows short
    assert out[11] == -100.0  # long black body, both shadows short


def test_long_line_warmup_is_zero():
    out = _ll(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    np.testing.assert_array_equal(out[:10], 0.0)  # TA-Lib lookback = 10


def test_long_line_short_frame_is_zero():
    # Fewer bars than the lookback -> BodyLong/ShadowShort averages are undefined -> all zero.
    out = _ll(frame([100.0, 101.0, 100.0], high=[101.5] * 3, low=[99.5] * 3, open_=[100.05] * 3))
    np.testing.assert_array_equal(out, 0.0)


def test_long_line_constant_frame_is_zero():
    # A flat frame has zero real body, so the body can never exceed the BodyLong threshold.
    c = [100.0] * 20
    out = _ll(frame(c, high=c, low=c, open_=c))
    np.testing.assert_array_equal(out, 0.0)


def test_long_line_short_body_rejected():
    # A short body (even with short shadows) fails the BodyLong test -> 0.
    c = [100.05] * 14
    o = [100.0] * 14  # body 0.05 (short)
    h = [100.07] * 14
    low = [99.98] * 14
    out = _ll(frame(c, high=h, low=low, open_=o))
    assert (out[10:] == 0.0).all()


def test_long_line_long_shadows_rejected():
    # A long body but with long shadows -> the shadow test fails -> 0.
    c = [102.0] * 14
    o = [100.0] * 14  # body 2.0 (long)
    h = [106.0] * 14  # upper shadow 4.0 (long)
    low = [96.0] * 14  # lower shadow 4.0 (long)
    out = _ll(frame(c, high=h, low=low, open_=o))
    assert (out[10:] == 0.0).all()


def test_long_line_output_contract():
    out = INDICATORS.create("long_line").compute(
        frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN)
    )
    assert list(out.columns) == ["long_line"]
    assert set(np.unique(out["long_line"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
