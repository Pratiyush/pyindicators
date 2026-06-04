"""Abandoned Baby parity — EXACT integer match vs ``talib.CDLABANDONEDBABY``.

Candles are integer-exact, so no tolerance: ``np.testing.assert_array_equal`` against
``talib.CDLABANDONEDBABY`` on the deterministic frame and on genuine AAPL daily bars. The real
fixture has no abandoned-baby occurrence (the pattern needs a doji isolated by gaps on both
sides), so a hand-built frame with both a bullish and a bearish occurrence pins the non-zero
branches and the ``penetration`` parameter.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.abandoned_baby import abandoned_baby  # noqa: F401  (fires @register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df, penetration=0.3):
    our = (
        INDICATORS.create("abandoned_baby", penetration=penetration)
        .compute(df)["abandoned_baby"]
        .to_numpy()
    )
    ref = talib.CDLABANDONEDBABY(*_ohlc(df), penetration).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def _embedded_frame():
    """10 warm bars then a bullish occurrence (12->14) and a bearish one (15->17)."""
    o = [100.0] * 10
    c = [101.0] * 10
    h = [101.2] * 10
    low = [99.8] * 10
    # Bullish: black #1, doji gapped down, white #3 gapped up closing deep into #1.
    o += [110.0, 95.0, 96.0]
    c += [100.0, 95.05, 106.0]
    h += [110.2, 95.3, 106.2]
    low += [99.8, 94.7, 95.8]
    # Bearish: white #1, doji gapped up, black #3 gapped down closing deep into #1.
    o += [100.0, 115.0, 114.0]
    c += [110.0, 115.05, 106.0]
    h += [110.2, 115.3, 114.2]
    low += [99.8, 114.7, 105.8]
    return pd.DataFrame({"open": o, "high": h, "low": low, "close": c})


def test_abandoned_baby_parity_synthetic():
    _check(deterministic_frame())


def test_abandoned_baby_parity_real():
    _check(real_frame())  # genuine AAPL daily bars (no occurrence -> all zeros, still exact)


def test_abandoned_baby_parity_embedded_both_directions():
    df = _embedded_frame()
    ref = talib.CDLABANDONEDBABY(*_ohlc(df), 0.3).astype("float64")
    assert np.any(ref == 100) and np.any(ref == -100)  # fixture hits both directions
    _check(df)


@pytest.mark.parametrize("penetration", [0.0, 0.1, 0.3, 0.5, 0.9])
def test_abandoned_baby_parity_penetration(penetration):
    _check(_embedded_frame(), penetration=penetration)
    _check(deterministic_frame(), penetration=penetration)
