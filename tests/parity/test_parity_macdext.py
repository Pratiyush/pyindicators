"""MACDEXT parity — exact (modulo float64 rounding) vs ``talib.MACDEXT`` (all matypes 0).

TA-Lib's ``MACDEXT`` with the default matypes (0 = SMA) is a plain-rolling-mean construction,
identical to our ``base.sma`` composition. Because nothing is recursive there is no seeding
drift, so agreement is exact up to floating-point rounding on the mutual finite overlap. The
only wrinkle is warm-up *alignment*: TA-Lib withholds the MACD line until the signal also
seeds (combined lookback), while we emit the line one signal-window earlier — masking to the
finite intersection makes that cosmetic difference irrelevant.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.trend.macdext import macdext  # noqa: F401  (import fires @register)

talib = pytest.importorskip("talib")


def _p(our, ref, *, rtol=1e-7, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _talib_macdext(close, fast=12, slow=26, signal=9):
    # All matypes default to 0 (SMA) — the convention our composition mirrors.
    return talib.MACDEXT(
        close.to_numpy(dtype="float64"),
        fastperiod=fast,
        fastmatype=0,
        slowperiod=slow,
        slowmatype=0,
        signalperiod=signal,
        signalmatype=0,
    )


@pytest.mark.parametrize("frame_fn", [deterministic_frame, real_frame])
def test_macdext_parity_talib(frame_fn):
    df = frame_fn()
    out = INDICATORS.create("macdext", fast=12, slow=26, signal=9).compute(df)
    tmacd, tsig, thist = _talib_macdext(df["close"], 12, 26, 9)
    _p(out["macdext"], tmacd)
    _p(out["macdext_signal"], tsig)
    _p(out["macdext_hist"], thist)


@pytest.mark.parametrize("fast,slow,signal", [(8, 21, 5), (12, 26, 9), (10, 30, 13)])
def test_macdext_parity_talib_param_sweep(fast, slow, signal):
    df = deterministic_frame()
    out = INDICATORS.create("macdext", fast=fast, slow=slow, signal=signal).compute(df)
    tmacd, tsig, thist = _talib_macdext(df["close"], fast, slow, signal)
    _p(out["macdext"], tmacd)
    _p(out["macdext_signal"], tsig)
    _p(out["macdext_hist"], thist)
