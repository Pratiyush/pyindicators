"""High Wave — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.high_wave import high_wave  # noqa: F401  (import fires @register)

# 10 warm-up bars (body ~0.5, range ~1) then a white high-wave, then a black high-wave.
# High-wave: tiny body, both shadows > 2x the body (here body 0.1, shadows ~0.5).
_OPEN = [100.0] * 10 + [100.0, 100.1]
_CLOSE = [100.5] * 10 + [100.1, 100.0]
_HIGH = [100.7] * 10 + [100.7, 100.7]
_LOW = [99.8] * 10 + [99.5, 99.5]


def _hw(df):
    return INDICATORS.create("high_wave").compute(df)["high_wave"].to_numpy()


def test_high_wave_white_and_black():
    out = _hw(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    assert out[10] == 100.0  # small white body, both shadows longer than 2x the body
    assert out[11] == -100.0  # small black body, both shadows longer than 2x the body


def test_high_wave_warmup_is_zero():
    out = _hw(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    np.testing.assert_array_equal(out[:10], 0.0)  # TA-Lib lookback = BodyShort period (10)


def test_high_wave_short_frame_is_zero():
    # Fewer bars than the lookback -> the BodyShort average is undefined -> all zero.
    out = _hw(frame([100.0, 100.0, 100.0], high=[101.0] * 3, low=[99.0] * 3, open_=[100.05] * 3))
    np.testing.assert_array_equal(out, 0.0)


def test_high_wave_constant_frame_is_zero():
    # A flat frame has zero shadows, so no shadow can exceed the threshold -> all zero.
    c = [100.0] * 20
    out = _hw(frame(c, high=c, low=c, open_=c))
    np.testing.assert_array_equal(out, 0.0)


def test_high_wave_short_shadows_rejected():
    # Tiny body but shadows not longer than 2x the body -> not a high-wave -> 0.
    c = [100.0] * 14
    o = [99.95] * 14  # body 0.05
    h = [100.02] * 14  # upper shadow 0.02 (< 2x body)
    low = [99.93] * 14  # lower shadow 0.02
    out = _hw(frame(c, high=h, low=low, open_=o))
    assert (out[10:] == 0.0).all()


def test_high_wave_long_body_rejected():
    # Long body with long shadows -> body fails the BodyShort test -> 0.
    c = [102.0] * 14
    o = [100.0] * 14  # body 2.0 (long)
    h = [105.0] * 14  # upper shadow 3.0
    low = [97.0] * 14  # lower shadow 3.0
    out = _hw(frame(c, high=h, low=low, open_=o))
    assert (out[10:] == 0.0).all()


def test_high_wave_output_contract():
    out = INDICATORS.create("high_wave").compute(
        frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN)
    )
    assert list(out.columns) == ["high_wave"]
    assert set(np.unique(out["high_wave"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
