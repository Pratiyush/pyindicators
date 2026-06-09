"""mansfield_rs — RS line normalized by its own MA (zero-line crossings)."""

import numpy as np
import pandas as pd

from pyindicators import INDICATORS


def _frame(close, bench=None):
    df = pd.DataFrame({"open": close, "high": close, "low": close, "close": close, "volume": close})
    if bench is not None:
        df["benchmark"] = np.asarray(bench, dtype="float64")
    return df


def test_mansfield_zero_when_matching_benchmark():
    n = 120
    close = pd.Series(np.linspace(10, 20, n))
    out = INDICATORS.create("mansfield_rs", length=20).compute(_frame(close, close))
    assert abs(out["mansfield_rs"].iloc[-1]) < 1e-9  # rp == 1 -> (1/1 - 1)*100 == 0


def test_mansfield_positive_when_outperforming():
    n = 120
    close = pd.Series(np.linspace(10, 30, n))  # rising fast
    bench = pd.Series(np.linspace(10, 15, n))  # rising slow
    out = INDICATORS.create("mansfield_rs", length=20).compute(_frame(close, bench))
    assert out["mansfield_rs"].iloc[-1] > 0


def test_mansfield_causal_with_benchmark():
    n = 80
    close = pd.Series(np.linspace(10, 25, n))
    bench = pd.Series(np.linspace(10, 18, n))
    ind = INDICATORS.create("mansfield_rs", length=10)
    full = ind.compute(_frame(close, bench))
    trunc = ind.compute(_frame(close.iloc[:40], bench.iloc[:40]))
    pd.testing.assert_series_equal(
        full["mansfield_rs"].iloc[:40], trunc["mansfield_rs"], check_names=False
    )
