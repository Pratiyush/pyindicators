"""TOS StDevAll parity vs pandas-ta — synthetic and real data.

pandas-ta ``tos_stdevall`` default = length=None (all bars), stds=[1,2,3], ddof=1 -> 7 columns.
We fit with the same ``numpy.polyfit`` and a sample stdev, so the match is essentially exact
(tight rtol). Compared on the full overlap (no warm-up: the fit spans every bar).
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.statistics.tos_stdevall import tos_stdevall  # noqa: F401  (registers indicator)

pta = pytest.importorskip("pandas_ta_classic")

# our output column -> pandas-ta column (default 7-column layout).
_PAIRS = (
    ("tos_stdevall_lr", "TOS_STDEVALL_LR"),
    ("tos_stdevall_l_1", "TOS_STDEVALL_L_1"),
    ("tos_stdevall_u_1", "TOS_STDEVALL_U_1"),
    ("tos_stdevall_l_2", "TOS_STDEVALL_L_2"),
    ("tos_stdevall_u_2", "TOS_STDEVALL_U_2"),
    ("tos_stdevall_l_3", "TOS_STDEVALL_L_3"),
    ("tos_stdevall_u_3", "TOS_STDEVALL_U_3"),
)


def _p(our, ref, *, rtol=1e-6, atol=1e-6, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _check(df):
    out = INDICATORS.create("tos_stdevall").compute(df)
    ref = pta.tos_stdevall(df["close"])
    for ours, theirs in _PAIRS:
        _p(out[ours], ref[theirs])


def test_tos_stdevall_parity_synthetic():
    _check(deterministic_frame())


def test_tos_stdevall_parity_real():
    _check(real_frame())
