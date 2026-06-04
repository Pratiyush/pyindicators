"""Rainbow Charts parity vs pandas-ta — synthetic and real data.

pandas-ta's ``rainbow`` returns a 10-column frame ``RAINBOW_1..RAINBOW_10`` where each column
is the SMA of the previous one (default ``length=2``). We compare ribbon-for-ribbon on the
tail. pandas-ta returns ``None`` if the series is shorter than ``length * num_ribbons`` (its
``verify_series`` guard); both fixtures here are far longer than that, so the oracle is defined.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.trend.rainbow import NUM_RIBBONS  # noqa: F401  (ensures registration)

pta = pytest.importorskip("pandas_ta_classic")


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _check(df, length=2):
    ours = INDICATORS.create("rainbow", length=length).compute(df)
    ref = pta.rainbow(df["close"], length=length)
    assert ref is not None and ref.shape[1] == NUM_RIBBONS
    for i in range(1, NUM_RIBBONS + 1):
        _p(ours[f"rainbow_{i}"], ref[f"RAINBOW_{i}"])


def test_rainbow_parity_synthetic():
    _check(deterministic_frame())


def test_rainbow_parity_real():
    _check(real_frame())


def test_rainbow_parity_synthetic_length3():
    # A non-default period to exercise the cascade away from the length=2 default.
    _check(deterministic_frame(), length=3)
