"""Harami — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.harami import harami  # noqa: F401  (import fires @register)

# 11 warm-up bars (body 2.0) so BodyLong/BodyShort averages are 2.0 by the time the pattern
# forms at bar 12 -> bar 13.
_WARM = 11
_WO = [100.0] * _WARM
_WC = [102.0] * _WARM
_WH = [102.2] * _WARM
_WL = [99.8] * _WARM


def _har(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("harami").compute(df)["harami"].to_numpy()


def test_harami_bullish_strict():
    # Long black (110->100) then a small white body strictly inside -> +100 (prev black).
    o = _WO + [110.0, 102.0]
    c = _WC + [100.0, 103.0]
    h = _WH + [110.5, 103.5]
    low = _WL + [99.5, 101.5]
    assert _har(o, h, low, c)[12] == 100.0


def test_harami_bearish_strict():
    # Long white (100->110) then a small black body strictly inside -> -100 (prev white).
    o = _WO + [100.0, 108.0]
    c = _WC + [110.0, 107.0]
    h = _WH + [110.5, 108.5]
    low = _WL + [99.5, 106.5]
    assert _har(o, h, low, c)[12] == -100.0


def test_harami_one_edge_touch_is_80():
    # Current body touches the previous body's top edge (strict bottom) -> partial score 80.
    o = _WO + [110.0, 108.5]
    c = _WC + [100.0, 110.0]
    h = _WH + [110.5, 110.5]
    low = _WL + [99.5, 108.0]
    assert _har(o, h, low, c)[12] == 80.0


def test_harami_warmup_is_zero():
    o = _WO + [110.0, 102.0]
    c = _WC + [100.0, 103.0]
    h = _WH + [110.5, 103.5]
    low = _WL + [99.5, 101.5]
    np.testing.assert_array_equal(_har(o, h, low, c)[:11], 0.0)  # TA-Lib lookback = 11


def test_harami_output_contract():
    o = _WO + [110.0, 102.0]
    c = _WC + [100.0, 103.0]
    h = _WH + [110.5, 103.5]
    low = _WL + [99.5, 101.5]
    out = INDICATORS.create("harami").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["harami"]
    assert set(np.unique(out["harami"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
