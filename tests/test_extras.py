"""Edge coverage for base.cache_key, common spec helpers, and resample/align branches."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pyindicators import (
    INDICATORS,
    Timeframe,
    align_to_base,
    parse_spec,
    rename_outputs,
    resample_ohlcv,
)


def _daily(n, start="2020-01-06"):
    close = np.arange(1.0, n + 1)
    ts = pd.date_range(start, periods=n, freq="D", tz="UTC")
    return pd.DataFrame({"ts": ts, "open": close, "high": close + 0.5, "low": close - 0.5,
                         "close": close, "close_raw": close, "volume": 100.0, "adj_factor": 1.0})


def test_cache_key_stable_and_sensitive():
    a = INDICATORS.create("sma", period=50)
    b = INDICATORS.create("sma", period=50)
    c = INDICATORS.create("sma", period=200)
    assert a.cache_key() == b.cache_key() != c.cache_key()
    assert a.cache_key().startswith("sma-")


def test_parse_spec_string_keeps_non_numeric_value():
    assert parse_spec("rs_line:benchmark=SPY") == ("rs_line", {"benchmark": "SPY"})


def test_rename_outputs_suffix_and_noop():
    df = _daily(10)
    sma = INDICATORS.create("sma", period=3)
    assert list(rename_outputs(sma.compute(df), sma).columns) == ["sma_3"]
    obv = INDICATORS.create("obv")  # primary_param None -> unchanged
    assert list(rename_outputs(obv.compute(df), obv).columns) == ["obv"]


def test_resample_empty_and_month_label():
    assert resample_ohlcv(_daily(0), Timeframe.WEEK).empty
    out = resample_ohlcv(_daily(90), Timeframe.MONTH, base=Timeframe.DAY)
    assert len(out) >= 2 and (out["ts"].dt.day == 1).all()


def test_align_requires_ts_and_prefix_none():
    with pytest.raises(ValueError):
        align_to_base(_daily(5).drop(columns=["ts"]), _daily(5))
    base = _daily(20)
    wk = resample_ohlcv(base, Timeframe.WEEK, base=Timeframe.DAY)[["ts", "close"]].rename(
        columns={"close": "wk_close"}
    )
    merged = align_to_base(wk, base)  # prefix=None branch
    assert "wk_close" in merged.columns and len(merged) == len(base)
