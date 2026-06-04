"""VPA Climactic Bars — golden + edge cases (deterministic; no reference library).

There is no library oracle for this VSA "climax" rule, so the golden tests assert the
closed-form definition directly: a flag fires iff (ultra-high volume) AND (wide spread) AND
(a strict new ``length``-bar extreme close). Frames are hand-built so the exact firing bar is
known, mirroring the candle / aobv flag-test style.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.volume.vpa_climactic_bars import (  # noqa: F401  (import fires @register)
    vpa_climactic_bars,
)

# length=5 throughout: 5 quiet warm-up bars seed SMA(volume)/SMA(range), then a signal bar at
# index 5. The signal bar's own volume/range are INCLUDED in its trailing SMA window
# (window = bars 1..5), which the thresholds below account for.
_LEN = 5
_W_CLOSE = [100.0, 101.0, 102.0, 103.0, 104.0]  # gently rising -> prior_max(@5) = 104
_W_HIGH = [c + 0.5 for c in _W_CLOSE]  # range = 1.0 each warm-up bar
_W_LOW = [c - 0.5 for c in _W_CLOSE]
_W_VOL = [1000.0] * _LEN


def _flag(close, high, low, volume, **kw):
    df = frame(close, high=high, low=low, volume=volume)
    return INDICATORS.create("vpa_climactic_bars", length=_LEN, **kw).compute(df)[
        "vpa_climactic_bars"
    ].to_numpy()


def _seq(close_bar, high_bar, low_bar, vol_bar):
    """Warm-up bars then one signal bar; returns (close, high, low, volume) lists."""
    return (
        _W_CLOSE + [close_bar],
        _W_HIGH + [high_bar],
        _W_LOW + [low_bar],
        _W_VOL + [vol_bar],
    )


def test_buying_climax_fires():
    # New high close (110 > prior_max 104), wide range (10 > 1.5*SMA=4.2), huge volume
    # (10000 > 2*SMA=5600) -> buying climax at index 5.
    c, h, low, v = _seq(110.0, 115.0, 105.0, 10000.0)
    out = _flag(c, h, low, v)
    assert out[_LEN] == 1.0
    np.testing.assert_array_equal(out[:_LEN], 0.0)  # warm-up never fires


def test_selling_climax_fires():
    # New low close (90 < prior_min 100), wide range, huge volume -> selling climax at index 5.
    c, h, low, v = _seq(90.0, 95.0, 85.0, 10000.0)
    out = _flag(c, h, low, v)
    assert out[_LEN] == 1.0
    np.testing.assert_array_equal(out[:_LEN], 0.0)


def test_high_volume_but_narrow_spread_is_zero():
    # Huge volume and a new high close, but the spread is normal (range 1.0, not wide) -> 0.
    c, h, low, v = _seq(110.0, 110.5, 109.5, 10000.0)
    out = _flag(c, h, low, v)
    assert out[_LEN] == 0.0


def test_wide_spread_but_normal_volume_is_zero():
    # Wide range and a new high close, but volume is ordinary (1000, not ultra-high) -> 0.
    c, h, low, v = _seq(110.0, 115.0, 105.0, 1000.0)
    out = _flag(c, h, low, v)
    assert out[_LEN] == 0.0


def test_climactic_volume_and_spread_without_new_extreme_is_zero():
    # Ultra volume AND wide spread, but the close (103) stays INSIDE the prior range
    # [100, 104] -> not a new extreme -> not a climax (the trend gate blocks it).
    c, h, low, v = _seq(103.0, 108.0, 98.0, 10000.0)
    out = _flag(c, h, low, v)
    assert out[_LEN] == 0.0


def test_constant_frame_never_fires():
    # Flat OHLCV: no spread and no new extreme -> never a climax.
    n = 30
    c = [100.0] * n
    out = _flag(c, c, c, [1000.0] * n)
    np.testing.assert_array_equal(out, 0.0)


def test_short_frame_all_zero():
    # Fewer bars than ``length`` -> SMA / prior-window never fill -> all warm-up zeros (no NaN).
    c, h, low, v = [100.0, 101.0, 102.0], [101.0, 102.0, 103.0], [99.0, 100.0, 101.0], [
        1000.0,
        9000.0,
        9000.0,
    ]
    out = _flag(c, h, low, v)
    np.testing.assert_array_equal(out, 0.0)


def test_thresholds_are_strict_inequalities():
    # Volume exactly at the threshold (not strictly above) must NOT fire. With warm-up vol=1000
    # and signal vol V, SMA(@5)=(4*1000+V)/5; the gate is V > vol_k*SMA. Solve V == vol_k*SMA
    # for vol_k=2: V == 2*(4000+V)/5 -> 5V == 8000+2V -> V == 8000/3. At that exact value the
    # strict ``>`` is False -> 0; nudging V up by 1 fires.
    v_eq = 8000.0 / 3.0
    c, h, low, _ = _seq(110.0, 115.0, 105.0, 0.0)
    at = _flag(c, h, low, _W_VOL + [v_eq])
    above = _flag(c, h, low, _W_VOL + [v_eq + 1.0])
    assert at[_LEN] == 0.0  # exactly at threshold: strict > fails
    assert above[_LEN] == 1.0  # just above: fires


def test_params_tighten_and_loosen():
    # A borderline bar: vol 6000, range 5.0, new high. Defaults (vol_k 2 -> thr 5600,
    # range_k 1.5 -> thr 4.2) fire it; raising vol_k to 5 (thr 14000) suppresses it.
    c, h, low, v = _seq(110.0, 112.5, 107.5, 6000.0)
    assert _flag(c, h, low, v)[_LEN] == 1.0
    assert _flag(c, h, low, v, vol_k=5.0)[_LEN] == 0.0


def test_output_contract_strictly_binary_and_finite():
    df = deterministic_frame(300)
    out = INDICATORS.create("vpa_climactic_bars").compute(df)
    assert list(out.columns) == ["vpa_climactic_bars"]
    assert out["vpa_climactic_bars"].dtype == np.float64
    assert len(out) == 300
    vals = out["vpa_climactic_bars"].to_numpy()
    assert np.isfinite(vals).all()  # finite everywhere (warm-up is 0, never NaN)
    assert set(np.unique(vals)) <= {0.0, 1.0}  # strictly binary
