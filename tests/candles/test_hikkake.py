"""Hikkake — golden + edge cases (deterministic; no reference library).

The fixtures below were each cross-checked against ``talib.CDLHIKKAKE`` (see the parity test);
here they are hard-coded so the structural behaviour is pinned without needing TA-Lib at all.
Five warm-up bars precede every pattern (TA-Lib lookback = 5). The inside bar sits at index 5,
the breakout (setup) at index 6, and a later close confirms it at index 7.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.hikkake import hikkake  # noqa: F401  (import fires @register)

# Five flat warm-up bars; the wide bar (index 4) and inside bar (index 5) set up the break.
_WO = [10.0] * 5
_WC = [10.0] * 5


def _hik(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("hikkake").compute(df)["hikkake"].to_numpy()


def test_hikkake_bullish_setup_is_100():
    # Wide bar (idx4), inside bar (idx5), then a lower-high lower-low break (idx6) -> +100.
    o = _WO + [10.0, 10.0]
    h = [11.0, 11.0, 11.0, 11.0, 20.0] + [18.0, 17.0]
    low = [9.0, 9.0, 9.0, 9.0, 5.0] + [7.0, 6.0]
    c = _WC + [10.0, 10.0]
    assert _hik(o, h, low, c)[6] == 100.0


def test_hikkake_bearish_setup_is_minus_100():
    # Inside bar (idx5) then a higher-high higher-low break (idx6) -> -100 (reversal sign).
    o = _WO + [10.0, 10.0]
    h = [11.0, 11.0, 11.0, 11.0, 20.0] + [18.0, 19.0]
    low = [9.0, 9.0, 9.0, 9.0, 5.0] + [7.0, 8.0]
    c = _WC + [10.0, 10.0]
    assert _hik(o, h, low, c)[6] == -100.0


def test_hikkake_bullish_confirmation_is_200():
    # +100 setup at idx6 (inside-bar high 18); idx7 closes above it -> +200 confirmation.
    o = _WO + [10.0, 10.0, 10.0, 10.0]
    h = [11.0, 11.0, 11.0, 11.0, 20.0] + [18.0, 17.0, 17.0, 17.0]
    low = [9.0, 9.0, 9.0, 9.0, 5.0] + [7.0, 6.0, 6.0, 6.0]
    c = _WC + [10.0, 10.0, 19.0, 10.0]
    out = _hik(o, h, low, c)
    assert out[6] == 100.0
    assert out[7] == 200.0


def test_hikkake_bearish_confirmation_is_minus_200():
    # -100 setup at idx6 (inside-bar low 7); idx7 closes below it -> -200 confirmation.
    o = _WO + [10.0, 10.0, 10.0, 10.0]
    h = [11.0, 11.0, 11.0, 11.0, 20.0] + [18.0, 19.0, 19.0, 19.0]
    low = [9.0, 9.0, 9.0, 9.0, 5.0] + [7.0, 8.0, 8.0, 8.0]
    c = _WC + [10.0, 10.0, 6.0, 10.0]
    out = _hik(o, h, low, c)
    assert out[6] == -100.0
    assert out[7] == -200.0


def test_hikkake_constant_frame_is_zero():
    # No strict inside bar can form when every high/low is identical -> all zeros.
    flat = [10.0] * 12
    np.testing.assert_array_equal(_hik(flat, flat, flat, flat), 0.0)


def test_hikkake_short_frame_is_zero():
    # Fewer bars than the lookback (5) -> no emittable bar, all zeros.
    o = [10.0, 10.0, 10.0, 10.0, 10.0]
    h = [11.0, 12.0, 11.0, 10.0, 9.0]
    low = [9.0, 8.0, 9.0, 10.0, 11.0]
    c = [10.0, 10.0, 10.0, 10.0, 10.0]
    np.testing.assert_array_equal(_hik(o, h, low, c), 0.0)


def test_hikkake_warmup_is_zero():
    # The first five bars (TA-Lib lookback) are always 0, regardless of geometry.
    o = _WO + [10.0, 10.0]
    h = [11.0, 11.0, 11.0, 11.0, 20.0] + [18.0, 17.0]
    low = [9.0, 9.0, 9.0, 9.0, 5.0] + [7.0, 6.0]
    c = _WC + [10.0, 10.0]
    np.testing.assert_array_equal(_hik(o, h, low, c)[:5], 0.0)


def test_hikkake_output_contract():
    o = _WO + [10.0, 10.0, 10.0, 10.0]
    h = [11.0, 11.0, 11.0, 11.0, 20.0] + [18.0, 17.0, 17.0, 17.0]
    low = [9.0, 9.0, 9.0, 9.0, 5.0] + [7.0, 6.0, 6.0, 6.0]
    c = _WC + [10.0, 10.0, 19.0, 10.0]
    out = INDICATORS.create("hikkake").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["hikkake"]
    assert set(np.unique(out["hikkake"].to_numpy())) <= {-200.0, -100.0, 0.0, 100.0, 200.0}
