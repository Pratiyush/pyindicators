"""Marubozu — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.marubozu import marubozu  # noqa: F401  (import fires @register)

# 10 warm-up bars (small body 0.2, range 1.0) then white marubozu, black marubozu, then a
# long body WITH a big upper shadow (not a marubozu).
_OPEN = [100.0] * 10 + [100.0, 102.0, 100.0]
_CLOSE = [100.2] * 10 + [102.0, 100.0, 102.0]
_HIGH = [100.5] * 10 + [102.0, 102.0, 103.0]
_LOW = [99.5] * 10 + [100.0, 100.0, 100.0]


def _marubozu(df):
    return INDICATORS.create("marubozu").compute(df)["marubozu"].to_numpy()


def test_marubozu_white_and_black():
    out = _marubozu(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    assert out[10] == 100.0  # long white body, no shadows
    assert out[11] == -100.0  # long black body, no shadows


def test_marubozu_long_shadow_rejected():
    out = _marubozu(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    assert out[12] == 0.0  # long body but a big upper shadow disqualifies it


def test_marubozu_warmup_is_zero():
    out = _marubozu(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    np.testing.assert_array_equal(out[:10], 0.0)  # TA-Lib lookback = BodyLong period (10)


def test_marubozu_output_contract():
    out = INDICATORS.create("marubozu").compute(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    assert list(out.columns) == ["marubozu"]
    assert set(np.unique(out["marubozu"].to_numpy())) <= {-100.0, 0.0, 100.0}
