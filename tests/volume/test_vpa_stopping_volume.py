"""VPA Stopping Volume (VSA) — golden + edge cases.

Import the module directly so ``@INDICATORS.register`` fires without the package __init__.
Stopping Volume is a golden-only structural pattern (no reference oracle); these tests pin its
four conditions (downtrend, down-bar, high volume, close off the low) one at a time.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.volume import vpa_stopping_volume as _mod  # noqa: F401  (fires @register)


def _scenario():
    """A 6-bar falling series, then a wide high-volume down-bar that closes near its high.

    Bars 0..4 step down so by bar 5 the close is below the 5-bar trend SMA and below the
    prior close (down-bar). Bar 5 has a wide range [90, 100] but closes at 99 (top of the
    range -> long lower shadow) on 5x the average volume -> stopping volume fires.
    """
    close = [105.0, 103.0, 101.0, 99.0, 97.0, 95.0]
    high = [105.0, 103.0, 101.0, 99.0, 97.0, 100.0]
    low = [105.0, 103.0, 101.0, 99.0, 97.0, 90.0]
    volume = [100.0, 100.0, 100.0, 100.0, 100.0, 500.0]
    return close, high, low, volume


def _run(close, high, low, volume, **kw):
    f = frame(close, high=high, low=low, volume=volume)
    params = {"trend_length": 5, "vol_length": 5, "vol_mult": 1.5, "close_loc": 0.5}
    params.update(kw)
    return INDICATORS.create("vpa_stopping_volume", **params).compute(f)["vpa_stopping_volume"]


def test_golden_stopping_volume_fires():
    close, high, low, volume = _scenario()
    out = _run(close, high, low, volume)
    # Only the final bar (wide, high-volume, closes off the low, after a downtrend) fires.
    assert out.iloc[-1] == 1.0
    assert (out.iloc[:-1] == 0.0).all()


def test_output_is_strictly_binary():
    close, high, low, volume = _scenario()
    out = _run(close, high, low, volume)
    assert set(np.unique(out.to_numpy())) <= {0.0, 1.0}
    assert not out.isna().any()  # warm-up emits 0, never NaN


def test_warmup_bars_are_zero_not_nan():
    # Before the trend/volume SMA windows fill there is no signal -> 0 (not NaN).
    close, high, low, volume = _scenario()
    out = _run(close, high, low, volume)
    # trend_length=5 means the SMA is NaN for bars 0..3; those must be 0.
    assert (out.iloc[:4] == 0.0).all()


def test_low_volume_does_not_fire():
    # Same wide down-bar closing off its low, but volume is only average -> no high-volume.
    close, high, low, _ = _scenario()
    volume = [100.0] * 6  # final bar no longer a spike
    out = _run(close, high, low, volume)
    assert out.iloc[-1] == 0.0


def test_up_bar_does_not_fire():
    # High volume + wide range + closes off the low, but it's an UP-bar (close > prior close).
    close = [105.0, 103.0, 101.0, 99.0, 97.0, 99.0]  # last close 99 > prior 97 -> up-bar
    high = [105.0, 103.0, 101.0, 99.0, 97.0, 100.0]
    low = [105.0, 103.0, 101.0, 99.0, 97.0, 90.0]
    volume = [100.0, 100.0, 100.0, 100.0, 100.0, 500.0]
    out = _run(close, high, low, volume)
    assert out.iloc[-1] == 0.0


def test_close_on_the_low_does_not_fire():
    # High-volume wide down-bar, but it closes at the LOW (no lower shadow) -> not stopping.
    close, high, _, volume = _scenario()
    low = [105.0, 103.0, 101.0, 99.0, 97.0, 95.0]  # final low == close 95 -> close at the low
    high = list(high)
    high[-1] = 100.0
    out = _run(close, high, low, volume)
    assert out.iloc[-1] == 0.0


def test_no_downtrend_does_not_fire():
    # A high-volume wide down-bar closing off its low, but in an UPtrend: the close stays
    # above its trend SMA, so the downtrend gate blocks the signal. Only that gate differs
    # from the golden positive case.
    close = [90.0, 92.0, 94.0, 96.0, 98.0, 97.0]  # last close 97 > SMA(5)=95.4 -> no downtrend
    high = [90.0, 92.0, 94.0, 96.0, 98.0, 100.0]
    low = [90.0, 92.0, 94.0, 96.0, 98.0, 90.0]  # close 97 is off the low of [90,100]
    volume = [100.0, 100.0, 100.0, 100.0, 100.0, 500.0]
    out = _run(close, high, low, volume)
    assert out.iloc[-1] == 0.0  # 97 is NOT below the trend mean -> no downtrend context
    # Sanity: it IS a high-volume down-bar closing off its low (only the trend gate blocks it).
    f = frame(close, high=high, low=low, volume=volume)
    c = f["close"]
    assert c.iloc[-1] < c.iloc[-2]  # down-bar
    assert (c.iloc[-1] - f["low"].iloc[-1]) / (f["high"].iloc[-1] - f["low"].iloc[-1]) >= 0.5


def test_stricter_close_loc_can_suppress():
    # Raising close_loc to 0.95 demands the close be in the top 5% of the range; a close at
    # the range midpoint then fails the wick test.
    close = [105.0, 103.0, 101.0, 99.0, 97.0, 95.0]
    high = [105.0, 103.0, 101.0, 99.0, 97.0, 100.0]
    low = [105.0, 103.0, 101.0, 99.0, 97.0, 90.0]  # close 95 is exactly mid of [90,100]
    volume = [100.0, 100.0, 100.0, 100.0, 100.0, 500.0]
    assert _run(close, high, low, volume, close_loc=0.5).iloc[-1] == 1.0  # mid passes 0.5
    assert _run(close, high, low, volume, close_loc=0.95).iloc[-1] == 0.0  # mid fails 0.95


def test_short_frame_all_zero():
    # Fewer bars than the SMA window -> nothing can fire -> all zeros (no NaN).
    out = _run([100.0, 99.0, 98.0], [100.0, 99.0, 98.0], [100.0, 99.0, 98.0], [1.0, 1.0, 1.0])
    assert (out == 0.0).all()
    assert not out.isna().any()


def test_does_not_mutate_input():
    close, high, low, volume = _scenario()
    f = frame(close, high=high, low=low, volume=volume)
    before = f.copy(deep=True)
    INDICATORS.create("vpa_stopping_volume", trend_length=5, vol_length=5).compute(f)
    import pandas as pd

    pd.testing.assert_frame_equal(f, before)
