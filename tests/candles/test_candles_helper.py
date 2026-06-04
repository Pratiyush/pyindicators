"""``_candles`` helper — geometry, the 11 CandleSettings, and the averaging contract.

These tests pin the foundation that every ``CDL*`` pattern reuses: the per-bar geometry, the
exact ``candle_average`` window (``AvgPeriod`` bars ending at ``i-1``; ``AvgPeriod == 0`` means
the current bar), the ``Shadows`` divisor of 2.0, and the error paths.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pyindicators.candles._candles import (
    CANDLE_SETTINGS,
    both_shadows,
    candle_average,
    candle_color,
    hl_range,
    lower_shadow,
    real_body,
    upper_shadow,
)


def _frame():
    # 12 bars; each white with body 1.0, range 3.0, upper shadow 1.0, lower shadow 1.0.
    base = np.arange(10.0, 22.0)
    return pd.DataFrame(
        {
            "open": base,
            "high": base + 2.0,
            "low": base - 1.0,
            "close": base + 1.0,
            "volume": np.ones(12),
        }
    )


def test_geometry_components():
    df = _frame()
    np.testing.assert_array_equal(real_body(df).to_numpy(), 1.0)  # |close - open|
    np.testing.assert_array_equal(hl_range(df).to_numpy(), 3.0)  # high - low
    np.testing.assert_array_equal(upper_shadow(df).to_numpy(), 1.0)  # high - max(o, c)
    np.testing.assert_array_equal(lower_shadow(df).to_numpy(), 1.0)  # min(o, c) - low
    np.testing.assert_array_equal(both_shadows(df).to_numpy(), 2.0)  # upper + lower


def test_candle_color_white_black_and_doji():
    df = pd.DataFrame(
        {
            "open": [10.0, 12.0, 11.0],
            "high": [13.0, 13.0, 13.0],
            "low": [9.0, 9.0, 9.0],
            "close": [11.0, 10.0, 11.0],  # white, black, doji(open==close)
            "volume": [1.0, 1.0, 1.0],
        }
    )
    np.testing.assert_array_equal(candle_color(df).to_numpy(), [1, -1, 1])  # doji -> white


def test_average_period_zero_uses_current_bar():
    df = _frame()
    # ShadowLong = (RealBody, 0, 1.0): no averaging, no warm-up -> equals the current body.
    np.testing.assert_array_equal(candle_average(df, "ShadowLong").to_numpy(), 1.0)
    # ShadowVeryLong = (RealBody, 0, 2.0): factor scales the current bar.
    np.testing.assert_array_equal(candle_average(df, "ShadowVeryLong").to_numpy(), 2.0)


def test_average_window_ends_at_previous_bar():
    df = _frame()
    # BodyLong = (RealBody, 10, 1.0): first 10 bars NaN, then mean of the prior 10 bodies.
    bl = candle_average(df, "BodyLong").to_numpy()
    assert np.isnan(bl[:10]).all()  # TA-Lib lookback = AvgPeriod
    assert bl[10] == 1.0  # mean of ten unit bodies (bars 0..9), excludes the current bar
    assert bl[11] == 1.0


def test_shadows_divisor_is_two():
    df = _frame()
    # ShadowShort = (Shadows, 10, 1.0): divisor 2.0 -> mean(both_shadows)/2 = 2.0/2 = 1.0.
    ss = candle_average(df, "ShadowShort").to_numpy()
    assert ss[10] == 1.0


def test_all_eleven_settings_present_and_computable():
    df = _frame()
    expected = {
        "BodyLong", "BodyVeryLong", "BodyShort", "BodyDoji", "ShadowLong", "ShadowVeryLong",
        "ShadowShort", "ShadowVeryShort", "Near", "Far", "Equal",
    }
    assert set(CANDLE_SETTINGS) == expected
    for name in CANDLE_SETTINGS:
        assert isinstance(candle_average(df, name), pd.Series)


def test_unknown_setting_raises():
    with pytest.raises(KeyError):
        candle_average(_frame(), "NoSuchSetting")


def test_unknown_range_type_raises(monkeypatch):
    from pyindicators.candles import _candles

    bad = _candles.CandleSetting("NotARange", 10, 1.0)
    monkeypatch.setitem(_candles.CANDLE_SETTINGS, "BadSetting", bad)
    with pytest.raises(ValueError, match="unknown range type"):
        candle_average(_frame(), "BadSetting")
