"""QQE parity vs pandas-ta-classic — synthetic and real data.

pandas-ta's ``qqe`` returns (with EMA mamode + defaults) the columns
``QQE_14_5_4.236`` (active line), ``QQE_14_5_4.236_RSIMA`` (smoothed-RSI basis),
``QQEl_14_5_4.236`` / ``QQEs_14_5_4.236`` (sparse long/short signal lines). We map our
four outputs onto those.

Seeding note: our RSI/EMA chain seeds the inner Wilder-length EMAs from a clean
``length``-valid-value window, whereas pandas-ta-classic's ``rma`` seeds one bar earlier from
a NaN-contaminated mean. The two converge to machine precision once warm, so parity is checked
index-aligned on the warmed tail (tail=60, rtol/atol 1e-5) — comfortably tight given the
observed residual (~1e-9 or better on the active line, ~1e-14 on the basis).
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.momentum.qqe import qqe  # noqa: F401  (import fires @INDICATORS.register)

pta = pytest.importorskip("pandas_ta_classic")

_PROPS = "14_5_4.236"  # default length_smooth_factor (ema mamode -> empty mode prefix)
_MAP = {
    "qqe": f"QQE_{_PROPS}",
    "qqe_rsima": f"QQE_{_PROPS}_RSIMA",
    "qqe_long": f"QQEl_{_PROPS}",
    "qqe_short": f"QQEs_{_PROPS}",
}


def _tail_parity(our, ref, *, tail=60, rtol=1e-5, atol=1e-5, min_overlap=40):
    """Compare index-aligned, masked to finite overlap, on the last ``tail`` warmed bars."""
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    idx = np.flatnonzero(mask)
    assert idx.size >= min_overlap
    idx = idx[-tail:]
    np.testing.assert_allclose(our[idx], ref[idx], rtol=rtol, atol=atol)


def _check(df):
    ours = INDICATORS.create("qqe").compute(df)
    ref = pta.qqe(df["close"], length=14, smooth=5, factor=4.236)
    for our_col, ref_col in _MAP.items():
        _tail_parity(ours[our_col], ref[ref_col])


def test_qqe_parity_synthetic():
    _check(deterministic_frame())


def test_qqe_parity_real():
    _check(real_frame())
