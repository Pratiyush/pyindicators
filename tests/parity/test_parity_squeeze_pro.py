"""TTM Squeeze Pro parity vs pandas_ta_classic — synthetic and real data.

pandas-ta returns the momentum as a dynamically-named first column
(``SQZPRO_<bb_length>_<bb_std>_...``) plus integer 0/1 flag columns
``SQZPRO_ON_WIDE / _ON_NORMAL / _ON_NARROW / _OFF / _NO``. We compare our float64 columns
against those; the flags coincide exactly (integers vs the same integers as floats), while
the momentum is SMA-of-diff so it agrees to floating tolerance after its warm-up.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")

# our output name -> pandas-ta column suffix for the integer flag columns
_FLAG_MAP = {
    "sqz_on_wide": "SQZPRO_ON_WIDE",
    "sqz_on_normal": "SQZPRO_ON_NORMAL",
    "sqz_on_narrow": "SQZPRO_ON_NARROW",
    "sqz_off": "SQZPRO_OFF",
    "sqz_no": "SQZPRO_NO",
}


def _close(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _check(df):
    ours = INDICATORS.create("squeeze_pro").compute(df)
    ref = pta.squeeze_pro(df["high"], df["low"], df["close"])
    # Momentum column is the dynamically-named first column in the pandas-ta frame.
    _close(ours["sqz"], ref.iloc[:, 0])
    # Flags must match exactly (integer 0/1 == the same value as float64).
    for ours_name, ref_name in _FLAG_MAP.items():
        np.testing.assert_array_equal(
            ours[ours_name].to_numpy(), ref[ref_name].to_numpy().astype("float64")
        )


def test_squeeze_pro_parity_synthetic():
    _check(deterministic_frame())


def test_squeeze_pro_parity_real():
    _check(real_frame())
