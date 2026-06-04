"""Williams Alligator parity — synthetic and real data.

No reference library ships the SMMA-based Alligator, so (as with RSL) the oracle is its
closed-form definition built from pandas-ta-classic's own ``rma``: each line is
``pta.rma((high + low) / 2, length)``. SMMA == Wilder's RMA, and our ``base.rma`` matches
pandas-ta ``rma`` exactly, so parity is exact (rtol ~0). The canonical forward offsets
(jaw +8 / teeth +5 / lips +3) are deliberately omitted on our side to stay causal, so the
oracle is likewise unshifted.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.momentum.alligator import alligator  # noqa: F401  (import fires @register)

pta = pytest.importorskip("pandas_ta_classic")

_PERIODS = {"alligator_jaw": 13, "alligator_teeth": 8, "alligator_lips": 5}


def _p(our, ref, *, rtol=1e-12, atol=1e-12, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _check(df):
    out = INDICATORS.create("alligator", jaw=13, teeth=8, lips=5).compute(df)
    median = (df["high"] + df["low"]) / 2.0
    for col, length in _PERIODS.items():
        _p(out[col], pta.rma(median, length=length))  # closed-form SMMA oracle


def test_alligator_parity_synthetic():
    _check(deterministic_frame())


def test_alligator_parity_real():
    _check(real_frame())
