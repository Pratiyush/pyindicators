"""ROC1 parity vs pandas-ta ``roc(length=1)`` — synthetic and real data.

ROC1 is the one-bar special case of ROC, so the canonical oracle is pandas-ta ``roc`` with
``length=1`` (``100 * mom(close, 1) / close.shift(1)``, the same closed form). Prices in both
fixtures are >= 1, so our zero-base guard never fires and parity is exact (bar the warm-up
NaN). Importing the module registers ROC1 (utils is not yet wired into the top-level package).
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.utils import roc1  # noqa: F401  (import fires @INDICATORS.register)

pta = pytest.importorskip("pandas_ta_classic")


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_roc1_parity_synthetic():
    df = deterministic_frame()
    _p(INDICATORS.create("roc1").compute(df)["roc1"], pta.roc(df["close"], length=1))


def test_roc1_parity_real():
    df = real_frame()
    _p(INDICATORS.create("roc1").compute(df)["roc1"], pta.roc(df["close"], length=1))
