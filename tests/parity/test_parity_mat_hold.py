"""Mat Hold parity — EXACT integer match vs ``talib.CDLMATHOLD``.

Candles are integer-exact, so this asserts equality with no tolerance. Mat Hold is a rare
five-bar continuation pattern that does not fire on the synthetic walk or the AAPL fixture, so
beyond the standard deterministic/real sweeps this test also feeds a constructed frame that
makes ``talib.CDLMATHOLD`` emit a genuine +100 — proving we match TA-Lib on an actual firing,
not only on the trivial all-zero case.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, frame, real_frame
from pyindicators import INDICATORS
from pyindicators.candles.mat_hold import mat_hold  # noqa: F401  (fires @register)

talib = pytest.importorskip("talib")

# TA-Lib lookback for CDLMATHOLD: max(BodyShort, BodyLong) avgPeriod (10) + 4 prior bars.
_LOOKBACK = 14


def _ohlc(df):
    return tuple(df[c].to_numpy(dtype="float64") for c in ("open", "high", "low", "close"))


def _check(df, penetration=0.5):
    our = (
        INDICATORS.create("mat_hold", penetration=penetration)
        .compute(df)["mat_hold"]
        .to_numpy()
    )
    ref = talib.CDLMATHOLD(*_ohlc(df), penetration=penetration).astype("float64")
    assert ref.shape == our.shape
    # Force the first 'lookback' bars to 0 to match TA-Lib's warm-up convention exactly.
    ref[:_LOOKBACK] = 0.0
    np.testing.assert_array_equal(our, ref)
    return ref


def _firing_frame():
    """A frame engineered so ``talib.CDLMATHOLD`` emits a +100 (the pattern is too rare to
    occur in the synthetic walk or the AAPL fixture)."""
    warm = 14
    wo = [100.0] * warm
    wc = [105.0] * warm  # moderate warm-up body so BodyLong/BodyShort average settles near 5
    wh = [105.2] * warm
    wl = [99.8] * warm
    po = [100.0, 113.0, 111.0, 110.0, 109.0]
    pc = [110.0, 112.0, 109.0, 108.0, 115.0]
    ph = [110.2, 113.5, 111.2, 110.2, 115.2]
    pl = [99.8, 111.5, 108.8, 107.8, 108.8]
    return frame(wc + pc, high=wh + ph, low=wl + pl, open_=wo + po)


def test_mat_hold_parity_synthetic():
    _check(deterministic_frame())


def test_mat_hold_parity_real():
    _check(real_frame())  # genuine AAPL daily bars


def test_mat_hold_parity_constructed_firing():
    ref = _check(_firing_frame())
    assert np.any(ref == 100.0)  # the constructed frame contains a genuine Mat Hold firing


def test_mat_hold_parity_penetration_03():
    # Match TA-Lib exactly under a non-default penetration too.
    _check(deterministic_frame(), penetration=0.3)
    _check(_firing_frame(), penetration=0.3)
