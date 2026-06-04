"""Connors RSI parity — no single library ships CRSI, so we cross-check its components.

The dominant + only library-available piece is the Wilder RSI: we verify our price-RSI(3)
against pandas-ta ``rsi`` on synthetic and real data, then rebuild the *whole* composite using
pandas-ta's RSI for both RSI legs (price and streak) and assert it equals our ``crsi``. That
puts an external oracle under both RSI calls; the streak and percent-rank legs are pinned to
Connors' closed form (see ``tests/momentum/test_crsi.py``).
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.momentum.crsi import _percent_rank, _streak
from pyindicators.momentum.roc import roc

pta = pytest.importorskip("pandas_ta_classic")


def _p(our, ref, *, rtol=1e-6, atol=1e-6, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    # tail + rtol: Wilder's RMA is EMA-seeded-by-SMA, so early bars diverge until it converges.
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _crsi_via_pta(close):
    # Canonical CRSI(3,2,100) rebuilt with pandas-ta supplying both Wilder-RSI legs.
    price_rsi = pta.rsi(close, length=3)
    streak_rsi = pta.rsi(_streak(close), length=2)
    rank = _percent_rank(roc(close, length=1), 100)
    return (price_rsi + streak_rsi + rank) / 3.0


def test_price_rsi_component_parity_synthetic():
    df = deterministic_frame()
    ours = INDICATORS.create("rsi", length=3).compute(df)["rsi"]
    _p(ours, pta.rsi(df["close"], length=3))


def test_price_rsi_component_parity_real():
    df = real_frame()
    ours = INDICATORS.create("rsi", length=3).compute(df)["rsi"]
    _p(ours, pta.rsi(df["close"], length=3))


def test_crsi_full_parity_synthetic():
    df = deterministic_frame()
    ours = INDICATORS.create("crsi", rsi_length=3, streak_length=2, rank_length=100).compute(df)["crsi"]
    _p(ours, _crsi_via_pta(df["close"]))


def test_crsi_full_parity_real():
    df = real_frame()
    ours = INDICATORS.create("crsi", rsi_length=3, streak_length=2, rank_length=100).compute(df)["crsi"]
    _p(ours, _crsi_via_pta(df["close"]))
