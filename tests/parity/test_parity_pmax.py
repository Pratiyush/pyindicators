"""PMAX parity vs pandas-ta(_classic) — synthetic and real data.

pandas-ta's ``pmax`` returns only the trail line (no direction), so we compare our ``pmax``
column against it. The only formula difference is the ATR seed: our True Range defines bar 0
as ``H-L`` whereas pandas-ta leaves it NaN, so the Wilder-smoothed ATR (and thus the bands)
start one bar apart and *converge*. We therefore compare the converged tail — over the last
~50 bars the two agree to ~1e-13 on both synthetic and real frames.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")


def _parity_tail(our, ref, *, tail=50, rtol=1e-7, atol=1e-7):
    # Wilder-ATR seed differs by one bar (see module docstring): assert on the converged tail.
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:][-tail:], ref[-n:][-tail:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= tail - 5  # tail should be fully warmed up
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_pmax_parity_synthetic():
    df = deterministic_frame()
    ours = INDICATORS.create("pmax", length=10, mult=3.0, mamode="ema").compute(df)["pmax"]
    ref = pta.pmax(df["high"], df["low"], df["close"], length=10, multiplier=3.0, mamode="ema")
    _parity_tail(ours, ref)


def test_pmax_parity_real():
    df = real_frame()
    ours = INDICATORS.create("pmax", length=10, mult=3.0, mamode="ema").compute(df)["pmax"]
    ref = pta.pmax(df["high"], df["low"], df["close"], length=10, multiplier=3.0, mamode="ema")
    _parity_tail(ours, ref)


def test_pmax_parity_sma_mode():
    # SMA mode removes the EMA warm-up subtlety in the MA term; the ATR seed still converges.
    df = deterministic_frame()
    ours = INDICATORS.create("pmax", length=10, mult=2.0, mamode="sma").compute(df)["pmax"]
    ref = pta.pmax(df["high"], df["low"], df["close"], length=10, multiplier=2.0, mamode="sma")
    _parity_tail(ours, ref)
