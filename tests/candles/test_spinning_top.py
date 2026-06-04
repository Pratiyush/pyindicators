"""Spinning Top — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.spinning_top import spinning_top  # noqa: F401  (import fires @register)

# 10 warm-up bars (body 0.5, range ~1) then a white spinning top, then a black spinning top.
_OPEN = [100.0] * 10 + [100.0, 100.1]
_CLOSE = [100.5] * 10 + [100.1, 100.0]
_HIGH = [100.7] * 10 + [100.6, 100.6]
_LOW = [99.8] * 10 + [99.4, 99.4]


def _spin(df):
    return INDICATORS.create("spinning_top").compute(df)["spinning_top"].to_numpy()


def test_spinning_top_white_and_black():
    out = _spin(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    assert out[10] == 100.0  # small white body, both shadows longer than the body
    assert out[11] == -100.0  # small black body, both shadows longer than the body


def test_spinning_top_warmup_is_zero():
    out = _spin(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    np.testing.assert_array_equal(out[:10], 0.0)  # TA-Lib lookback = BodyShort period (10)


def test_spinning_top_no_shadows_rejected():
    # Small body but (almost) no shadows -> shadows are not longer than the body -> 0.
    c = [100.0] * 12
    o = [99.9] * 12  # body 0.1
    h = [100.0] * 12  # upper shadow 0
    low = [99.9] * 12  # lower shadow 0
    out = _spin(frame(c, high=h, low=low, open_=o))
    assert (out[10:] == 0.0).all()


def test_spinning_top_output_contract():
    out = INDICATORS.create("spinning_top").compute(
        frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN)
    )
    assert list(out.columns) == ["spinning_top"]
    assert set(np.unique(out["spinning_top"].to_numpy())) <= {-100.0, 0.0, 100.0}
