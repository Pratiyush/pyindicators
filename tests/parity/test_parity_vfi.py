"""Volume Flow Indicator parity vs finta — synthetic and real data.

finta ``TA.VFI`` is the oracle: it implements the canonical Katsanos formula (typical-price
change vs a stdev cutoff, signed volume, capped + smoothed). ``pandas_ta_classic.vfi`` ships a
degenerate variant (cutoff = ``coef*close``, no stdev/sign) that returns all-zeros on normal
daily data, so it is unusable for parity. We reproduce finta exactly (0.0 max-abs diff).
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

finta = pytest.importorskip("finta")
TA = finta.TA


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _check(df):
    # finta defaults: period=130, smoothing_factor=3, factor=0.2, vfactor=2.5.
    ref = TA.VFI(df, period=130, smoothing_factor=3, factor=0.2, vfactor=2.5)
    out = INDICATORS.create(
        "vfi", period=130, smoothing=3, factor=0.2, vfactor=2.5
    ).compute(df)["vfi"]
    _p(out, ref)


def test_vfi_parity_synthetic():
    _check(deterministic_frame())


def test_vfi_parity_real_data():
    _check(real_frame())  # genuine AAPL daily bars


def test_vfi_parity_alt_params():
    # Non-default knobs must track finta too (shorter period exposes more of the curve).
    df = deterministic_frame()
    ref = TA.VFI(df, period=60, smoothing_factor=5, factor=0.15, vfactor=3.0)
    out = INDICATORS.create(
        "vfi", period=60, smoothing=5, factor=0.15, vfactor=3.0
    ).compute(df)["vfi"]
    _p(out, ref)
