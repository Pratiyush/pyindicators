"""Separating Lines parity — EXACT integer match vs ``talib.CDLSEPARATINGLINES``.

Checked on both the synthetic deterministic walk and genuine AAPL daily bars, aligned with no
tolerance (candles are integer-exact). This pattern is pure ±100/0 — there is no partial ±80
score — so the parity is a straight ``assert_array_equal``.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.separating_lines import (  # noqa: F401  (import fires @register)
    separating_lines,
)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("separating_lines").compute(df)["separating_lines"].to_numpy()
    ref = talib.CDLSEPARATINGLINES(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def test_separating_lines_parity_synthetic():
    _check(deterministic_frame())


def test_separating_lines_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDLSEPARATINGLINES(*_ohlc(df)).astype("float64")
    assert np.any(ref != 0)  # the real fixture actually triggers the pattern
    assert np.all(np.isin(ref, (-100.0, 0.0, 100.0)))  # pure ±100/0, no partial score
    _check(df)
