"""Parabolic SAR parity — pandas-ta (synthetic + real) and TA-Lib SAR (tail)."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

pta = pytest.importorskip("pandas_ta_classic")


def _p(our, ref, *, rtol=1e-6, atol=1e-6, tail=None, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    if tail is not None:
        our, ref = our[-tail:], ref[-tail:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _check_pandas_ta(df):
    ref = pta.psar(df["high"], df["low"], af0=0.02, max_af=0.2)
    out = INDICATORS.create("psar", af0=0.02, max_af=0.2).compute(df)
    combined = ref.iloc[:, 0].fillna(ref.iloc[:, 1])  # PSARl over PSARs = the SAR line
    _p(out["psar"], combined)
    _p(out["psar_af"], ref.iloc[:, 2])
    _p(out["psar_reversal"], ref.iloc[:, 3])


def test_psar_parity_pandas_ta_synthetic():
    _check_pandas_ta(deterministic_frame())


def test_psar_parity_pandas_ta_real():
    _check_pandas_ta(real_frame())  # genuine AAPL daily bars


def test_psar_parity_talib_tail():
    # TA-Lib SAR uses a slightly different initial-trend seed; converges on the tail.
    talib = pytest.importorskip("talib")
    df = real_frame()
    our = INDICATORS.create("psar").compute(df)["psar"]
    ref = talib.SAR(df["high"].to_numpy(), df["low"].to_numpy(), acceleration=0.02, maximum=0.2)
    _p(our, ref, tail=200, rtol=1e-3)
