"""Doji — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.doji import doji  # noqa: F401  (import fires @register)

# 11 warm-up bars (body 1.0, high-low 2.0) then a doji (tiny body) then a non-doji (big body).
_WARM = 11
_OPEN = [100.0] * _WARM + [100.0, 100.0]
_CLOSE = [101.0] * _WARM + [100.05, 100.5]
_HIGH = [101.5] * _WARM + [101.0, 101.0]
_LOW = [99.5] * _WARM + [99.0, 99.0]


def _doji(df):
    return INDICATORS.create("doji").compute(df)["doji"].to_numpy()


def test_doji_golden_hit_and_miss():
    out = _doji(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    assert out[11] == 100.0  # body 0.05 <= 0.1 * avg(high-low) = 0.2
    assert out[12] == 0.0  # body 0.5 > 0.2


def test_doji_warmup_is_zero():
    out = _doji(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    np.testing.assert_array_equal(out[:10], 0.0)  # TA-Lib lookback = BodyDoji period (10)


def test_doji_equal_open_close_is_doji():
    # open == close is the canonical doji; fires once the 10-bar average exists.
    c = [100.0] * 15
    out = _doji(frame(c, high=[101.0] * 15, low=[99.0] * 15, open_=[100.0] * 15))
    assert (out[10:] == 100.0).all()


def test_doji_output_contract():
    out = INDICATORS.create("doji").compute(frame(_CLOSE, high=_HIGH, low=_LOW, open_=_OPEN))
    assert list(out.columns) == ["doji"]
    assert set(np.unique(out["doji"].to_numpy())) <= {0.0, 100.0}
