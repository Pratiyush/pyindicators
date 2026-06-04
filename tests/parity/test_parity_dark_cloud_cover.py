"""Dark Cloud Cover parity — EXACT integer match vs ``talib.CDLDARKCLOUDCOVER``.

Synthetic + real AAPL bars, no tolerance (candles are integer-exact). The real fixture
exercises genuine gap-up reversals, where TA-Lib emits the -100 signal.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.dark_cloud_cover import dark_cloud_cover  # noqa: F401  (fires register)

talib = pytest.importorskip("talib")


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df, **kw):
    our = INDICATORS.create("dark_cloud_cover", **kw).compute(df)["dark_cloud_cover"].to_numpy()
    ref = talib.CDLDARKCLOUDCOVER(*_ohlc(df), **kw).astype("float64")
    assert ref.shape == our.shape
    np.testing.assert_array_equal(our, ref)


def _firing_frame():
    """A hand-built frame that actually triggers the -100 signal at bar 12."""
    warm = 11
    o = [100.0] * warm + [100.0, 112.0]
    c = [101.0] * warm + [110.0, 104.0]
    h = [101.2] * warm + [110.5, 112.5]
    low = [99.8] * warm + [99.5, 103.5]
    return frame(c, high=h, low=low, open_=o)


def test_dark_cloud_cover_parity_synthetic():
    _check(deterministic_frame())


def test_dark_cloud_cover_parity_real():
    df = real_frame()  # genuine AAPL daily bars
    ref = talib.CDLDARKCLOUDCOVER(*_ohlc(df)).astype("float64")
    assert np.any(ref == -100)  # the real fixture actually triggers the pattern
    _check(df)


def test_dark_cloud_cover_parity_firing_case():
    df = _firing_frame()
    ref = talib.CDLDARKCLOUDCOVER(*_ohlc(df)).astype("float64")
    assert ref[12] == -100  # sanity: the crafted frame fires in TA-Lib too
    _check(df)


@pytest.mark.parametrize("penetration", [0.1, 0.3, 0.5, 0.7, 0.9])
def test_dark_cloud_cover_parity_penetration(penetration):
    # The penetration factor must thread through to TA-Lib bit-exactly on real data.
    _check(real_frame(), penetration=penetration)
