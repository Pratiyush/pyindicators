"""Closing Marubozu — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.closing_marubozu import closing_marubozu  # noqa: F401 (fires @register)

# 10 warm-up bars (small body 0.2, range 1.0). Then:
#  [10] white, close at high, open with a lower shadow  -> closing marubozu (+100)
#  [11] black, close at low, open with an upper shadow  -> closing marubozu (-100)
#  [12] white, but a big UPPER (closing-side) shadow    -> rejected (0)
#  [13] long white body with both ends clean            -> closing marubozu (+100)
_OPEN = [100.0] * 10 + [101.0, 101.0, 100.0, 100.0]
_CLOSE = [100.2] * 10 + [103.0, 99.0, 102.0, 102.0]
_HIGH = [100.5] * 10 + [103.0, 102.0, 103.0, 102.0]
_LOW = [99.5] * 10 + [100.0, 99.0, 100.0, 100.0]


def _closing_marubozu(df):
    return INDICATORS.create("closing_marubozu").compute(df)["closing_marubozu"].to_numpy()


def test_closing_marubozu_white_close_at_high():
    out = _closing_marubozu(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    assert out[10] == 100.0  # long white body, close == high (no upper shadow); lower shadow ok


def test_closing_marubozu_black_close_at_low():
    out = _closing_marubozu(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    assert out[11] == -100.0  # long black body, close == low (no lower shadow); upper shadow ok


def test_closing_marubozu_closing_side_shadow_rejected():
    out = _closing_marubozu(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    assert out[12] == 0.0  # white but a big upper (closing-side) shadow disqualifies it


def test_closing_marubozu_clean_long_body():
    out = _closing_marubozu(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    assert out[13] == 100.0  # long white body with both ends clean is still a closing marubozu


def test_closing_marubozu_warmup_is_zero():
    out = _closing_marubozu(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    np.testing.assert_array_equal(out[:10], 0.0)  # TA-Lib lookback = BodyLong period (10)


def test_closing_marubozu_constant_frame_is_zero():
    # A flat frame has zero-length bodies: never a long body, so always 0 (and no NaNs).
    c = [100.0] * 30
    out = _closing_marubozu(frame(c, high=[100.0] * 30, low=[100.0] * 30, open_=[100.0] * 30))
    np.testing.assert_array_equal(out, 0.0)


def test_closing_marubozu_short_frame_is_zero():
    # Fewer bars than the lookback -> every bar is within the warm-up -> all 0.
    c = [100.0, 101.0, 100.0, 101.0, 100.0]
    out = _closing_marubozu(frame(c, high=[101.5] * 5, low=[99.5] * 5, open_=[100.5] * 5))
    np.testing.assert_array_equal(out, 0.0)


def test_closing_marubozu_output_contract():
    out = INDICATORS.create("closing_marubozu").compute(
        frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN)
    )
    assert list(out.columns) == ["closing_marubozu"]
    assert set(np.unique(out["closing_marubozu"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
