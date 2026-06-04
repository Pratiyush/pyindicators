"""Kicking parity — EXACT integer match vs ``talib.CDLKICKING`` (synthetic + real).

Kicking is rare (two opposite-colour marubozus with a strict gap), so the random/real
fixtures contain no occurrences; a hand-built frame that actually triggers ``±100`` is added
so the parity test exercises the pattern logic, not just the all-zero path.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.kicking import kicking  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("kicking").compute(df)["kicking"].to_numpy()
    ref = talib.CDLKICKING(*_ohlc(df)).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def _triggering_frame() -> pd.DataFrame:
    # 12 quiet warm-up bars (body 2.0, tiny shadows), then a bullish kicking (black->white,
    # gap up) and a bearish kicking (white->black, gap down) so both ±100 signs are covered.
    o = [100.0] * 12
    c = [102.0] * 12
    h = [102.1] * 12
    low = [99.9] * 12
    # bullish: black marubozu 110->100, then gapped-up white marubozu 120->130
    o += [110.0, 120.0]
    c += [100.0, 130.0]
    h += [110.05, 130.05]
    low += [99.95, 119.95]
    # a neutral spacer doji so the next pair starts clean
    o += [100.0]
    c += [100.0]
    h += [100.0]
    low += [100.0]
    # bearish: white marubozu 120->130, then gapped-down black marubozu 110->100
    o += [120.0, 110.0]
    c += [130.0, 100.0]
    h += [130.05, 110.05]
    low += [119.95, 99.95]
    return pd.DataFrame(
        {
            "open": o,
            "high": h,
            "low": low,
            "close": c,
            "volume": np.ones(len(c)),
        }
    )


def test_kicking_parity_synthetic():
    _check(deterministic_frame())


def test_kicking_parity_real():
    _check(real_frame())  # genuine AAPL daily bars


def test_kicking_parity_triggering():
    df = _triggering_frame()
    ref = talib.CDLKICKING(*_ohlc(df)).astype("float64")
    assert np.any(ref == 100) and np.any(ref == -100)  # both signs actually fire
    _check(df)
