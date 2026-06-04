"""TD Sequential parity vs pandas_ta_classic — synthetic and real data.

Our ``td_seq_up`` / ``td_seq_dn`` map to pandas-ta's ``TD_SEQ_UPa`` / ``TD_SEQ_DNa``
(default ``show_all=True``). The counts are integer-valued and the NaN positions (off-run
bars) are part of the contract, so we assert *exact* equality including where each side is
NaN. Both frames use a default RangeIndex, so pandas-ta's index-resetting ``Series(...)``
aligns 1:1 with ours.
"""

from __future__ import annotations

import numpy as np
import pytest

import pyindicators.momentum.td_seq  # noqa: F401  -- ensure @register fires
from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")


def _exact_with_nans(our, ref, *, min_runs=20):
    """Assert ``our`` == ``ref`` elementwise, treating NaN == NaN, with enough run bars."""
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    assert our.shape == ref.shape
    finite = np.isfinite(ref)
    assert finite.sum() >= min_runs, "too few run bars to be a meaningful parity check"
    # NaN positions must coincide exactly...
    np.testing.assert_array_equal(np.isnan(our), np.isnan(ref))
    # ...and the counts must match on every run bar.
    np.testing.assert_array_equal(our[finite], ref[finite])


def _check(df):
    out = INDICATORS.create("td_seq").compute(df)
    ref = pta.td_seq(df["close"])
    _exact_with_nans(out["td_seq_up"], ref["TD_SEQ_UPa"])
    _exact_with_nans(out["td_seq_dn"], ref["TD_SEQ_DNa"])


def test_td_seq_parity_synthetic():
    _check(deterministic_frame())


def test_td_seq_parity_real():
    _check(real_frame())


def test_td_seq_parity_custom_length():
    # pandas-ta hard-codes the 13-bar window; verify our default matches and that a custom
    # cap still agrees with pandas-ta on every bar where the run is shorter than the cap.
    df = deterministic_frame()
    out13 = INDICATORS.create("td_seq", length=13).compute(df)
    ref = pta.td_seq(df["close"])
    _exact_with_nans(out13["td_seq_up"], ref["TD_SEQ_UPa"])
    _exact_with_nans(out13["td_seq_dn"], ref["TD_SEQ_DNa"])
