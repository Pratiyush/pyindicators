"""Rickshaw Man — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.rickshaw_man import rickshaw_man  # noqa: F401  (import fires @register)

# 10 warm-up bars with a high-low range of 2.0 (and a small body) so the BodyDoji average is
# 0.1 * 2.0 = 0.2 and the Near average is 0.2 * 2.0 = 0.4 by the time the pattern forms at bar 10.
_WARM = 10
_WO = [100.0] * _WARM
_WC = [100.05] * _WARM
_WH = [101.0] * _WARM
_WL = [99.0] * _WARM


def _rm(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("rickshaw_man").compute(df)["rickshaw_man"].to_numpy()


def test_rickshaw_man_golden_hit():
    # Tiny body centred at the midpoint (100), both shadows long (~1.0 each > body 0.0).
    o = _WO + [100.02]
    c = _WC + [99.98]
    h = _WH + [101.0]
    low = _WL + [99.0]
    # body 0.04 <= BodyDoji avg 0.2; shadows ~1.0 > ShadowLong avg (= body 0.04); body straddles
    # midpoint 100 within Near band 0.4 -> +100.
    assert _rm(o, h, low, c)[10] == 100.0


def test_rickshaw_man_miss_body_off_centre():
    # Doji body with long shadows but the body sits near the low, not the midpoint -> 0.
    o = _WO + [99.30]
    c = _WC + [99.34]
    h = _WH + [101.0]
    low = _WL + [99.0]
    # midpoint is 100.0; body edges (~99.3) are far below midpoint - Near(0.4) = 99.6 -> miss.
    assert _rm(o, h, low, c)[10] == 0.0


def test_rickshaw_man_miss_short_shadow():
    # Doji body centred, but one shadow is not long (upper shadow ~0) -> 0.
    o = _WO + [100.0]
    c = _WC + [99.96]
    h = _WH + [100.0]  # no upper shadow above the body top (100.0)
    low = _WL + [98.0]
    assert _rm(o, h, low, c)[10] == 0.0


def test_rickshaw_man_miss_big_body():
    # Body too big to be a doji even if centred with long shadows -> 0.
    o = _WO + [100.5]
    c = _WC + [99.5]
    h = _WH + [101.5]
    low = _WL + [98.5]
    assert _rm(o, h, low, c)[10] == 0.0


def test_rickshaw_man_warmup_is_zero():
    o = _WO + [100.02]
    c = _WC + [99.98]
    h = _WH + [101.0]
    low = _WL + [99.0]
    np.testing.assert_array_equal(_rm(o, h, low, c)[:10], 0.0)  # TA-Lib lookback = 10


def test_rickshaw_man_constant_frame_is_zero():
    # A flat frame (no range, no shadows) is never a rickshaw man.
    c = [100.0] * 30
    out = _rm(c, c, c, c)
    np.testing.assert_array_equal(out, 0.0)


def test_rickshaw_man_short_frame_is_zero():
    # Fewer bars than the lookback -> all zeros (no average can form).
    c = [100.0, 100.5, 99.5, 100.2, 99.8]
    out = _rm(
        [100.1, 100.4, 99.6, 100.1, 99.9],
        [101.0, 101.0, 101.0, 101.0, 101.0],
        [99.0, 99.0, 99.0, 99.0, 99.0],
        c,
    )
    assert len(out) == 5
    np.testing.assert_array_equal(out, 0.0)


def test_rickshaw_man_output_contract():
    o = _WO + [100.02]
    c = _WC + [99.98]
    h = _WH + [101.0]
    low = _WL + [99.0]
    out = INDICATORS.create("rickshaw_man").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["rickshaw_man"]
    assert set(np.unique(out["rickshaw_man"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
