"""Long Run / Short Run / AMAT — golden + edge cases."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import frame
from pyindicators import INDICATORS

_UPTREND = frame(np.arange(1.0, 80.0))
_DOWNTREND = frame(np.arange(80.0, 1.0, -1.0))


@pytest.mark.parametrize("name", ["long_run", "short_run", "amat"])
def test_outputs_are_binary(name):
    out = INDICATORS.create(name).compute(_UPTREND)
    for col in out.columns:
        assert set(np.unique(out[col].to_numpy())) <= {0.0, 1.0}


def test_long_run_fires_on_uptrend():
    out = INDICATORS.create("long_run").compute(_UPTREND)["long_run"]
    assert out.iloc[-1] == 1.0  # fast & slow both rising
    sr = INDICATORS.create("short_run").compute(_UPTREND)["short_run"]
    assert sr.iloc[-1] == 0.0


def test_short_run_fires_on_downtrend():
    out = INDICATORS.create("short_run").compute(_DOWNTREND)["short_run"]
    assert out.iloc[-1] == 1.0  # fast & slow both falling
    lr = INDICATORS.create("long_run").compute(_DOWNTREND)["long_run"]
    assert lr.iloc[-1] == 0.0


def test_amat_columns_equal_standalone_runs():
    out = INDICATORS.create("amat").compute(_UPTREND)
    lr = INDICATORS.create("long_run").compute(_UPTREND)["long_run"]
    sr = INDICATORS.create("short_run").compute(_UPTREND)["short_run"]
    np.testing.assert_array_equal(out["amat_lr"].to_numpy(), lr.to_numpy())
    np.testing.assert_array_equal(out["amat_sr"].to_numpy(), sr.to_numpy())


def test_amat_sma_mode_runs():
    out = INDICATORS.create("amat", mamode="sma").compute(_UPTREND)
    assert out["amat_lr"].iloc[-1] == 1.0  # SMA path also detects the steady up-trend
