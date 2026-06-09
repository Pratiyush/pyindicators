"""Tests for the multi-timeframe helpers (S1.3): resample_ohlcv + align_to_base."""

import numpy as np
import pandas as pd
import pytest

from pyindicators import Timeframe, align_to_base, resample_ohlcv


def _daily(n=15, start="2021-01-04"):
    """Business-day OHLCV with a UTC ``ts`` column (monotonically rising prices)."""
    ts = pd.bdate_range(start, periods=n, tz="UTC")
    rng = np.arange(n, dtype="float64")
    return pd.DataFrame(
        {
            "ts": ts,
            "open": 100 + rng,
            "high": 101 + rng,
            "low": 99 + rng,
            "close": 100.5 + rng,
            "volume": 1000 + rng,
        }
    )


# --- resample_ohlcv ------------------------------------------------------------
def test_resample_rejects_downsample():
    with pytest.raises(ValueError, match="finer"):
        resample_ohlcv(_daily(), Timeframe.HOUR, base=Timeframe.DAY)


def test_resample_empty_returns_copy():
    empty = _daily(0)
    out = resample_ohlcv(empty, Timeframe.WEEK)
    assert out.empty and out is not empty


def test_resample_daily_to_weekly_agg():
    df = _daily(15)
    wk = resample_ohlcv(df, Timeframe.WEEK, base=Timeframe.DAY)
    assert list(wk.columns) == ["ts", "open", "high", "low", "close", "volume"]
    first_week = df[df["ts"] <= wk["ts"].iloc[0]]
    assert wk["open"].iloc[0] == first_week["open"].iloc[0]
    assert wk["high"].iloc[0] == first_week["high"].max()
    assert wk["low"].iloc[0] == first_week["low"].min()
    assert wk["close"].iloc[0] == first_week["close"].iloc[-1]
    assert wk["volume"].iloc[0] == first_week["volume"].sum()


def test_resample_carries_close_raw_and_adj_factor():
    df = _daily(10)
    df["close_raw"] = df["close"] * 0.9
    df["adj_factor"] = 0.9
    wk = resample_ohlcv(df, Timeframe.WEEK)
    assert "close_raw" in wk.columns and "adj_factor" in wk.columns


def test_resample_monthly_left_labelled():
    mo = resample_ohlcv(_daily(45), Timeframe.MONTH)
    assert (mo["ts"].dt.day == 1).all()


def test_resample_partial_dropped_vs_kept():
    df = _daily(8)  # one full week + a partial second week
    closed = resample_ohlcv(df, Timeframe.WEEK)
    withp = resample_ohlcv(df, Timeframe.WEEK, include_partial=True)
    assert len(withp) >= len(closed)
    assert (closed["ts"] <= df["ts"].iloc[-1]).all()


def test_resample_uses_datetimeindex_when_no_ts():
    df = _daily(10).set_index("ts")  # DatetimeIndex, no ts column
    wk = resample_ohlcv(df, Timeframe.WEEK)
    assert "ts" in wk.columns and len(wk) >= 1


# --- align_to_base -------------------------------------------------------------
def test_align_requires_ts():
    with pytest.raises(ValueError, match="ts"):
        align_to_base(pd.DataFrame({"x": [1]}), _daily(3))


def test_align_backward_asof_no_lookahead():
    df = _daily(15)
    wk = resample_ohlcv(df, Timeframe.WEEK, base=Timeframe.DAY)
    aligned = align_to_base(wk[["ts", "close"]], df, prefix="wk")
    assert "wk_close" in aligned.columns
    assert len(aligned) == len(df) and aligned.index.equals(df.index)
    assert pd.isna(aligned["wk_close"].iloc[0])  # before any weekly bar closed
    last_wk = wk[wk["ts"] <= df["ts"].iloc[-1]]
    assert aligned["wk_close"].iloc[-1] == last_wk["close"].iloc[-1]


def test_align_no_prefix():
    df = _daily(10)
    wk = resample_ohlcv(df, Timeframe.WEEK).rename(columns={"close": "wkclose"})
    aligned = align_to_base(wk[["ts", "wkclose"]], df)
    assert "wkclose" in aligned.columns and aligned.index.equals(df.index)
