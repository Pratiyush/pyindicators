"""VPA No Supply — structural "parity" against an independent closed-form reference.

GOLDEN-ONLY: no reference library (TA-Lib / pandas-ta / finta / ta / tulip) implements a VSA
No Supply primitive, so there is no external oracle to diff against. Instead we pin the rule
with an *independent* re-derivation: a plain-numpy reference that recomputes the three
conditions from shifted arrays (a different code path than the pandas implementation) and
must agree exactly on both the deterministic synthetic walk and real market data.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

# Import the module directly so its @INDICATORS.register decorator fires under any test order.
from pyindicators.volume import vpa_no_supply as _mod  # noqa: F401


def _reference(df) -> np.ndarray:
    """Independent numpy re-derivation of the No Supply rule (no pandas .shift)."""
    high = df["high"].to_numpy(dtype="float64")
    low = df["low"].to_numpy(dtype="float64")
    close = df["close"].to_numpy(dtype="float64")
    volume = df["volume"].to_numpy(dtype="float64")
    spread = high - low
    n = len(close)

    out = np.full(n, np.nan, dtype="float64")
    for i in range(2, n):
        down_close = close[i] < close[i - 1]
        narrow = (spread[i] < spread[i - 1]) and (spread[i] < spread[i - 2])
        low_vol = (volume[i] < volume[i - 1]) and (volume[i] < volume[i - 2])
        out[i] = 1.0 if (down_close and narrow and low_vol) else 0.0
    return out


def _check(df) -> None:
    ours = INDICATORS.create("vpa_no_supply").compute(df)["vpa_no_supply"].to_numpy()
    ref = _reference(df)
    # NaN warm-up must line up exactly, and every finite flag must match bit-for-bit.
    np.testing.assert_array_equal(np.isnan(ours), np.isnan(ref))
    mask = np.isfinite(ref)
    np.testing.assert_array_equal(ours[mask], ref[mask])
    # Output is a strict 0/1 indicator within its declared bounds.
    assert set(np.unique(ours[mask])).issubset({0.0, 1.0})


def test_vpa_no_supply_structural_synthetic():
    _check(deterministic_frame())


def test_vpa_no_supply_structural_real():
    _check(real_frame())
