"""Ichimoku parity vs pandas-ta — synthetic and real data.

pandas-ta's ``ichimoku`` returns a VISIBLE df whose Span A/B are forward-shifted by ``kijun``
(the look-ahead "cloud") and a separate future-indexed span df. We compare ONLY the unshifted
lines: tenkan/kijun come straight out of the visible df; for the spans we reconstruct pandas-ta's
PRE-shift values (span_a from its unshifted tenkan/kijun, span_b by un-shifting its visible
column back by ``kijun``). All series are masked to the finite overlap.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.trend.ichimoku import ichimoku  # noqa: F401  (fires @register for create())

pta = pytest.importorskip("pandas_ta_classic")

TENKAN, KIJUN, SENKOU = 9, 26, 52


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _check(df):
    out = INDICATORS.create(
        "ichimoku", tenkan=TENKAN, kijun=KIJUN, senkou=SENKOU
    ).compute(df)
    vis, _span = pta.ichimoku(
        df["high"], df["low"], df["close"], tenkan=TENKAN, kijun=KIJUN, senkou=SENKOU
    )
    its, iks = f"ITS_{TENKAN}", f"IKS_{KIJUN}"  # tenkan/kijun (unshifted in the visible df)
    isb = f"ISB_{KIJUN}"  # span_b column (forward-shifted by kijun in the visible df)
    _p(out["tenkan"], vis[its])
    _p(out["kijun"], vis[iks])
    # span_a unshifted == 0.5*(unshifted tenkan + unshifted kijun); span_b un-shifted back.
    _p(out["span_a"], 0.5 * (vis[its] + vis[iks]))
    _p(out["span_b"], vis[isb].shift(-KIJUN))


def test_ichimoku_parity_synthetic():
    _check(deterministic_frame())


def test_ichimoku_parity_real():
    _check(real_frame())  # genuine AAPL daily bars
