"""Edge-case unit tests for the indicator library.

Covers degenerate inputs (empty / single-row / sub-window), flat markets, zero-range
windows, zero volume, parameter-validation boundaries, missing columns, and the exact
semantics of tricky cases (RSI/MFI on a flat market are *undefined* -> NaN, not 100).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError

from pyindicators import INDICATORS

NAMES = INDICATORS.names()


def mk(close, *, high=None, low=None, open_=None, vol=None, start="2020-01-01") -> pd.DataFrame:
    close = np.asarray(close, dtype="float64")
    n = len(close)
    high = close if high is None else np.asarray(high, "float64")
    low = close if low is None else np.asarray(low, "float64")
    open_ = close if open_ is None else np.asarray(open_, "float64")
    vol = np.ones(n) if vol is None else np.asarray(vol, "float64")
    ts = pd.date_range(start, periods=n, freq="D", tz="UTC")
    return pd.DataFrame(
        {"ts": ts, "open": open_, "high": high, "low": low, "close": close,
         "close_raw": close, "volume": vol, "adj_factor": 1.0}
    )


# --------------------------------------------------------------------------- #
# Generic edge cases, parametrized over every registered indicator.
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("name", NAMES, ids=NAMES)
def test_empty_frame_returns_empty_with_columns(name):
    out = INDICATORS.create(name).compute(mk([]))
    assert len(out) == 0
    assert tuple(out.columns) == INDICATORS.get(name).outputs


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
def test_single_row_does_not_crash(name):
    out = INDICATORS.create(name).compute(mk([5.0]))
    assert len(out) == 1
    assert tuple(out.columns) == INDICATORS.get(name).outputs


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
def test_sub_window_last_row_is_nan(name):
    ind = INDICATORS.create(name)
    if ind.primary_param not in {"period", "window", "k"}:
        pytest.skip("no single window")
    req = ind.params[ind.primary_param]
    if req < 2:
        pytest.skip("window too small to under-fill")
    out = ind.compute(mk(np.arange(1.0, req)))  # length = req - 1
    # The primary (window-dependent) output is the first column; some indicators also
    # emit a non-windowed companion (e.g. ATR's raw `tr`) that is legitimately defined.
    assert pd.isna(out.iloc[-1, 0]), f"{name}: value before enough history"


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
def test_no_inf_on_flat_market(name):
    flat = mk([5.0] * 40)
    out = INDICATORS.create(name).compute(flat).to_numpy()
    assert not np.isinf(out).any(), f"{name} produced inf on a flat market"


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
def test_no_inf_on_zero_volume(name):
    z = mk(np.arange(1.0, 41.0), vol=[0.0] * 40)
    out = INDICATORS.create(name).compute(z).to_numpy()
    assert not np.isinf(out).any(), f"{name} produced inf on zero volume"


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
def test_does_not_mutate_input(name):
    df = mk(np.linspace(10, 20, 40), vol=np.arange(1, 41.0))
    before = df.copy(deep=True)
    INDICATORS.create(name).compute(df)
    pd.testing.assert_frame_equal(df, before)


# --------------------------------------------------------------------------- #
# Missing required column -> clear ValueError (covers _common.require_columns).
# --------------------------------------------------------------------------- #

_REQUIRED_COL = {
    "sma": "close", "ema": "close", "wma": "close", "sma_slope": "close", "macd": "close",
    "rsi": "close", "roc": "close", "momentum": "close", "stdev": "close", "bbands": "close",
    "rs_line": "close", "mansfield_rs": "close", "rs_rating": "close",
    "atr": "high", "adx": "high", "stoch": "high", "willr": "high", "cci": "high",
    "donchian": "high", "keltner": "high", "aroon": "high", "rolling_high": "high",
    "pct_from_high": "high", "rolling_low": "low", "pct_from_low": "low",
    "obv": "volume", "mfi": "volume", "vwap": "volume", "rvol": "volume", "vol_sma": "volume",
    "force_index": "volume", "ttm_squeeze": "high",
    "kama": "close", "hma": "close", "vortex": "high",
    "adl": "volume", "cmf": "volume", "williams_ad": "high",
}


@pytest.mark.parametrize("name", NAMES, ids=NAMES)
def test_missing_required_column_raises(name):
    col = _REQUIRED_COL[name]
    df = mk(np.arange(1.0, 11.0), vol=np.arange(1.0, 11.0)).drop(columns=[col])
    with pytest.raises(ValueError):
        INDICATORS.create(name).compute(df)


# --------------------------------------------------------------------------- #
# Parameter-validation boundaries (pydantic).
# --------------------------------------------------------------------------- #

_BAD_PARAMS = [
    ("sma", {"period": 0}), ("sma", {"period": -5}), ("ema", {"period": 0}),
    ("wma", {"period": 0}), ("rsi", {"period": 0}), ("roc", {"period": 0}),
    ("momentum", {"period": 0}), ("atr", {"period": 0}), ("adx", {"period": 0}),
    ("aroon", {"period": 0}), ("cci", {"period": 0}), ("willr", {"period": 0}),
    ("stoch", {"k": 0}), ("bbands", {"period": 1}), ("bbands", {"num_std": 0}),
    ("stdev", {"period": 1}), ("keltner", {"mult": 0}), ("donchian", {"window": 0}),
    ("rolling_high", {"window": 0}), ("rolling_low", {"window": 0}),
    ("rvol", {"window": 0}), ("vol_sma", {"period": 0}), ("mfi", {"period": 0}),
    ("mansfield_rs", {"period": 1}), ("vwap", {"anchor": "weekly"}),
]


@pytest.mark.parametrize("name,params", _BAD_PARAMS, ids=[f"{n}-{p}" for n, p in _BAD_PARAMS])
def test_invalid_params_rejected(name, params):
    with pytest.raises(ValidationError):
        INDICATORS.create(name, **params)


def test_extra_param_rejected():
    with pytest.raises(ValidationError):
        INDICATORS.create("sma", period=10, bogus=1)


def test_macd_requires_fast_lt_slow():
    with pytest.raises(ValidationError):
        INDICATORS.create("macd", fast=26, slow=12)
    INDICATORS.create("macd", fast=5, slow=10)  # valid


def test_rs_rating_length_and_empty_validation():
    with pytest.raises(ValidationError):
        INDICATORS.create("rs_rating", lookbacks=[1, 2], weights=[1.0])
    with pytest.raises(ValidationError):
        INDICATORS.create("rs_rating", lookbacks=[], weights=[])


# --------------------------------------------------------------------------- #
# Indicator-specific math edge cases.
# --------------------------------------------------------------------------- #

def test_rsi_flat_market_is_nan():
    out = INDICATORS.create("rsi", period=5).compute(mk([5.0] * 20))
    assert out["rsi"].iloc[6:].isna().all()  # undefined on no movement


def test_rsi_pure_gains_and_losses():
    up = INDICATORS.create("rsi", period=5).compute(mk(np.arange(1.0, 30)))
    np.testing.assert_allclose(up["rsi"].iloc[6:], 100.0)
    down = INDICATORS.create("rsi", period=5).compute(mk(np.arange(30.0, 1, -1)))
    np.testing.assert_allclose(down["rsi"].iloc[6:], 0.0)


def test_mfi_flat_market_is_nan():
    out = INDICATORS.create("mfi", period=5).compute(mk([5.0] * 20))
    assert out["mfi"].iloc[6:].isna().all()


def test_mfi_pure_inflow_is_100_outflow_is_0():
    up = INDICATORS.create("mfi", period=4).compute(mk(np.arange(1.0, 20)))
    assert np.isclose(up["mfi"].iloc[-1], 100.0)
    down = INDICATORS.create("mfi", period=4).compute(mk(np.arange(20.0, 1, -1)))
    assert np.isclose(down["mfi"].iloc[-1], 0.0)


def test_stoch_flat_is_nan_and_bounded():
    out = INDICATORS.create("stoch").compute(mk([5.0] * 40))
    assert out["stoch_k"].iloc[-1] != out["stoch_k"].iloc[-1]  # NaN (0/0 range)


def test_willr_flat_is_nan():
    out = INDICATORS.create("willr").compute(mk([5.0] * 40))
    assert pd.isna(out["willr"].iloc[-1])


def test_cci_flat_is_nan():
    out = INDICATORS.create("cci").compute(mk([5.0] * 40))
    assert pd.isna(out["cci"].iloc[-1])


def test_bbands_flat_collapses():
    out = INDICATORS.create("bbands", period=5).compute(mk([5.0] * 20))
    last = out.iloc[-1]
    assert last["bb_upper"] == last["bb_lower"] == last["bb_mid"] == 5.0
    assert last["bb_width"] == 0.0
    assert pd.isna(last["bb_pctb"])  # (close - lower)/(upper - lower) = 0/0


def test_atr_flat_is_zero():
    out = INDICATORS.create("atr", period=3).compute(mk([5.0] * 12))
    np.testing.assert_allclose(out["atr"].iloc[3:], 0.0)


def test_aroon_fresh_high_and_low():
    up = INDICATORS.create("aroon", period=4).compute(mk(np.arange(1.0, 12)))
    assert np.isclose(up["aroon_up"].iloc[-1], 100.0)  # new high on the last bar
    down = INDICATORS.create("aroon", period=4).compute(mk(np.arange(12.0, 1, -1)))
    assert np.isclose(down["aroon_down"].iloc[-1], 100.0)


def test_donchian_upper_ge_lower():
    out = INDICATORS.create("donchian", window=5).compute(mk(np.arange(1.0, 30)))
    valid = out.dropna()
    assert (valid["dc_upper"] >= valid["dc_lower"]).all()
    np.testing.assert_allclose(valid["dc_mid"], (valid["dc_upper"] + valid["dc_lower"]) / 2)


def test_obv_direction_sign():
    out = INDICATORS.create("obv").compute(
        mk([1.0, 2.0, 1.0], vol=[10, 10, 10])
    )
    np.testing.assert_allclose(out["obv"].to_numpy(), [0.0, 10.0, 0.0])


def test_vwap_cumulative_value():
    df = mk([2.0, 4.0], high=[2.0, 4.0], low=[2.0, 4.0], vol=[1.0, 3.0])
    out = INDICATORS.create("vwap").compute(df)
    # tp == close here; cumulative (2*1 + 4*3)/(1+3) = 14/4 = 3.5
    assert np.isclose(out["vwap"].iloc[-1], 3.5)


def test_rvol_constant_volume_is_one():
    out = INDICATORS.create("rvol", window=5).compute(mk(np.arange(1.0, 20), vol=[7.0] * 19))
    np.testing.assert_allclose(out["rvol"].iloc[5:], 1.0)


def test_sma_slope_flat_zero_and_ramp_constant():
    flat = INDICATORS.create("sma_slope", period=3, lookback=2).compute(mk([5.0] * 20))
    np.testing.assert_allclose(flat["sma_slope"].dropna(), 0.0)
    ramp = INDICATORS.create("sma_slope", period=3, lookback=2).compute(mk(np.arange(0.0, 20)))
    # SMA of a unit ramp rises 1/bar; slope over lookback == 1.0
    np.testing.assert_allclose(ramp["sma_slope"].dropna(), 1.0)


def test_rolling_extremes_window_one_is_identity():
    df = mk(np.arange(1.0, 6), high=np.arange(2.0, 7), low=np.arange(0.0, 5))
    hi = INDICATORS.create("rolling_high", window=1).compute(df)
    lo = INDICATORS.create("rolling_low", window=1).compute(df)
    np.testing.assert_allclose(hi["rolling_high"], df["high"])
    np.testing.assert_allclose(lo["rolling_low"], df["low"])


def test_rs_rating_short_frame_all_nan():
    out = INDICATORS.create("rs_rating").compute(mk(np.arange(1.0, 10)))  # << 252
    assert out["rs_rating"].isna().all()


def test_rs_rating_known_weighted_return():
    df = mk([10.0, 11.0, 12.0, 13.0])
    ind = INDICATORS.create("rs_rating", lookbacks=[1, 2], weights=[1.0, 1.0])
    out = ind.compute(df)
    # last bar: ((13/12 - 1) + (13/11 - 1)) / 2
    expected = ((13 / 12 - 1) + (13 / 11 - 1)) / 2
    assert np.isclose(out["rs_rating"].iloc[-1], expected)


def test_ema_seeds_with_first_value():
    out = INDICATORS.create("ema", period=1).compute(mk([3.0, 9.0, 6.0]))
    np.testing.assert_allclose(out["ema"].to_numpy(), [3.0, 9.0, 6.0])  # span=1 == price
