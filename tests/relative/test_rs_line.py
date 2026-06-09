"""rs_line — close/benchmark price relative (benchmark-aware, degrades to 1.0)."""

import numpy as np
import pandas as pd

from pyindicators import INDICATORS


def _frame(close, bench=None):
    df = pd.DataFrame({"open": close, "high": close, "low": close, "close": close, "volume": close})
    if bench is not None:
        df["benchmark"] = np.asarray(bench, dtype="float64")
    return df


def test_rs_line_is_ratio():
    close = pd.Series([10.0, 11.0, 12.0, 13.0])
    bench = pd.Series([10.0, 10.0, 12.0, 12.0])
    out = INDICATORS.create("rs_line").compute(_frame(close, bench))
    np.testing.assert_allclose(out["rs_line"].to_numpy(), (close / bench).to_numpy())


def test_rs_line_degenerate_without_benchmark():
    close = pd.Series([10.0, 11.0, 12.0])
    out = INDICATORS.create("rs_line").compute(_frame(close))
    np.testing.assert_allclose(out["rs_line"].to_numpy(), 1.0)
