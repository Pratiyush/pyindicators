"""Tests for the multi-timeframe resample + as-of alignment helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pyindicators import INDICATORS, OHLCV_COLUMNS, Timeframe, align_to_base, resample_ohlcv


def _daily(close, start="2020-01-06"):
    close = np.asarray(close, dtype="float64")
    n = len(close)
    ts = pd.date_range(start, periods=n, freq="D", tz="UTC")
    return pd.DataFrame(
        {"ts": ts, "open": close, "high": close + 0.5, "low": close - 0.5,
         "close": close, "close_raw": close, "volume": 100.0, "adj_factor": 1.0}
    )


def test_resample_daily_to_weekly_aggregates_correctly():
    # 2020-01-06 (Mon) .. 2020-01-17 (Fri): two full W-FRI buckets.
    df = _daily(np.arange(1, 13, dtype=float))  # close 1..12
    wk = resample_ohlcv(df, Timeframe.WEEK, base=Timeframe.DAY)
    assert list(wk.columns) == OHLCV_COLUMNS
    assert len(wk) == 2
    b1, b2 = wk.iloc[0], wk.iloc[1]
    # bucket 1: close 1..5
    assert (b1["open"], b1["close"], b1["volume"]) == (1.0, 5.0, 500.0)
    assert b1["high"] == 5.5 and b1["low"] == 0.5
    # bucket 2: close 6..12
    assert (b2["open"], b2["close"], b2["volume"]) == (6.0, 12.0, 700.0)
    assert b2["high"] == 12.5 and b2["low"] == 5.5


def test_resample_rejects_downsampling():
    df = _daily(np.arange(1, 6, dtype=float))
    with pytest.raises(ValueError):
        resample_ohlcv(df, Timeframe.HOUR, base=Timeframe.DAY)


def test_resample_drops_partial_last_bucket_by_default():
    # Ends on a Wednesday -> the final (Friday-labelled) week is still forming.
    df = _daily(np.arange(1, 11, dtype=float))  # 01-06 .. 01-15 (Wed)
    closed = resample_ohlcv(df, Timeframe.WEEK, base=Timeframe.DAY)
    withpart = resample_ohlcv(df, Timeframe.WEEK, base=Timeframe.DAY, include_partial=True)
    assert len(withpart) == len(closed) + 1


def test_align_to_base_has_no_lookahead():
    df = _daily(np.arange(1, 31, dtype=float))  # 30 daily bars
    wk = resample_ohlcv(df, Timeframe.WEEK, base=Timeframe.DAY)
    sma = INDICATORS.create("sma", period=2).compute(wk)
    wk_ind = wk[["ts"]].copy()
    wk_ind["src_ts"] = wk["ts"].astype("int64")  # carry the weekly bar's own timestamp
    wk_ind = pd.concat([wk_ind, sma], axis=1)

    aligned = align_to_base(wk_ind, df, prefix="wk")
    assert len(aligned) == len(df)
    assert aligned.index.equals(df.index)
    # Every base bar may only see a weekly bar whose timestamp is <= its own (no future).
    mask = aligned["wk_sma"].notna()
    assert mask.any()
    assert (aligned.loc[mask, "wk_src_ts"] <= df.loc[mask, "ts"].astype("int64")).all()
