"""Kicking-by-length parity — EXACT integer match vs ``talib.CDLKICKINGBYLENGTH``.

Candles are integer-exact, so this asserts equality with no tolerance on the deterministic and
real fixtures. Those fixtures never trigger this rare pattern (two opposite marubozu with a
gap), so a hand-built signal frame additionally exercises the ±100 branch — including the
longer-marubozu sign rule that distinguishes ``CDLKICKINGBYLENGTH`` from ``CDLKICKING`` — and
is likewise checked bit-for-bit against TA-Lib.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.kicking_by_length import (  # noqa: F401  (import fires @register)
    kicking_by_length,
)

talib = pytest.importorskip("talib")

# TA-Lib lookback for CDLKICKINGBYLENGTH (max(BodyLong, ShadowVeryShort) avg period + 1).
_LOOKBACK = 11


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df):
    our = INDICATORS.create("kicking_by_length").compute(df)["kicking_by_length"].to_numpy()
    ref = talib.CDLKICKINGBYLENGTH(*_ohlc(df)).astype("float64")
    ref[:_LOOKBACK] = 0.0  # force the warm-up bars to 0 to match TA-Lib's lookback
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def _signal_frame() -> pd.DataFrame:
    # 11 tiny warm-up bars, then opposite marubozu pairs with gaps that fire +100 and -100.
    warm = 11
    wo = [100.0] * warm
    wc = [100.1] * warm
    wh = [100.15] * warm
    wl = [99.95] * warm
    # bars 11-12: black maru (body 10) gaps up to a LONGER white maru (body 15) -> +100 at 12.
    # bar  13   : tiny neutral bar (breaks the chain so bar 14 starts a fresh pair).
    # bars 14-15: white maru (body 10) gaps down to a LONGER black maru (body 20) -> -100 at 15.
    o = wo + [120.0, 130.0, 100.05, 110.0, 100.0]
    c = wc + [110.0, 145.0, 100.05, 120.0, 80.0]
    h = wh + [120.0, 145.0, 100.10, 120.0, 100.0]
    low = wl + [110.0, 130.0, 100.00, 110.0, 80.0]
    return pd.DataFrame({"open": o, "high": h, "low": low, "close": c})


def test_kicking_by_length_parity_synthetic():
    _check(deterministic_frame())


def test_kicking_by_length_parity_real():
    _check(real_frame())  # genuine AAPL daily bars


def test_kicking_by_length_parity_signal_frame():
    df = _signal_frame()
    ref = talib.CDLKICKINGBYLENGTH(*_ohlc(df)).astype("float64")
    # Sanity: the hand-built frame genuinely fires both directions in TA-Lib.
    assert np.any(ref == 100) and np.any(ref == -100)
    _check(df)
