"""TTM Squeeze parity vs pandas-ta (default mode) — synthetic and real data.

We implement pandas-ta's *default* squeeze (lazybear=False, mamode="sma", tr=True). All the
pieces are SMA-based (no EMA/Wilder seeding), so the momentum line matches to full precision
on the finite overlap; the on/off/no flags are exact 0/1. pandas-ta names the momentum column
dynamically (``SQZ_<bb_length>_<bb_std>_<kc_length>_<kc_scalar>``) and the flags
``SQZ_ON`` / ``SQZ_OFF`` / ``SQZ_NO``.

KNOWN PINNED DIVERGENCE (exactly one bar, index ``kc_length - 1`` = 19): pandas-ta's
``true_range`` leaves bar 0 NaN, so its KC true-range SMA only becomes valid at index
``kc_length`` (20). Our ``base.true_range`` fills bar 0 with ``high - low`` (a divergence
documented in true_range.py to match finta/the bar-0 convention), so our KC is valid one bar
earlier. The momentum line is unaffected (no true_range). We therefore compare the flags from
index ``kc_length`` onward; everything from there matches exactly on both frames.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")


def _close_finite(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _check(df):
    ours = INDICATORS.create("squeeze").compute(df)
    ref = pta.squeeze(df["high"], df["low"], df["close"])
    # Momentum column is named SQZ_<bb_length>_<bb_std>_<kc_length>_<kc_scalar>; the flags
    # are SQZ_ON / SQZ_OFF / SQZ_NO. The momentum column is the remaining one.
    flags = {"SQZ_ON", "SQZ_OFF", "SQZ_NO"}
    mom_col = next(c for c in ref.columns if c not in flags)
    _close_finite(ours["squeeze"], ref[mom_col])
    # Flags: pandas-ta returns ints (0/1). Compare as floats from index kc_length onward to
    # skip the single TR-bar-0 warm-up boundary divergence documented in the module header.
    kc_length = 20
    for col, rcol in (("squeeze_on", "SQZ_ON"), ("squeeze_off", "SQZ_OFF"), ("squeeze_no", "SQZ_NO")):
        np.testing.assert_array_equal(
            ours[col].to_numpy()[kc_length:], ref[rcol].to_numpy()[kc_length:]
        )


def test_squeeze_parity_synthetic():
    _check(deterministic_frame())


def test_squeeze_parity_real():
    _check(real_frame())
