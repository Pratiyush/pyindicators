"""Volume-Weighted MACD parity vs finta ``EV_MACD`` — synthetic and real data.

We are a bit-exact closed-form replication of finta's EVWMA recurrence + ``adjust=True`` ewm
signal, so the tolerance is tight (this is exactness, not a papered-over EMA seed). finta 1.3
ships pandas<2.0 code (``Series.iteritems``, removed in pandas 2.x); we alias it to ``.items``
so the *actual* finta source runs as the oracle rather than substituting our own re-derivation.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

finta = pytest.importorskip("finta")
TA = finta.TA

# finta's EVWMA loop uses Series.iteritems() (gone in pandas 2.x); alias to .items() so it runs.
if not hasattr(pd.Series, "iteritems"):
    pd.Series.iteritems = pd.Series.items  # type: ignore[attr-defined]


def _p(our, ref, *, rtol=1e-9, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def _check(df, fast, slow, signal):
    ref = TA.EV_MACD(df, period_fast=fast, period_slow=slow, signal=signal)
    out = INDICATORS.create("vwmacd", fast=fast, slow=slow, signal=signal).compute(df)
    _p(out["vwmacd"], ref["MACD"])
    _p(out["vwmacd_signal"], ref["SIGNAL"])


def test_vwmacd_parity_synthetic():
    _check(deterministic_frame(), 12, 26, 9)


def test_vwmacd_parity_real():
    _check(real_frame(), 12, 26, 9)  # genuine AAPL daily bars


def test_vwmacd_parity_finta_defaults():
    # finta's own defaults (20/40/9) on both fixtures, to exercise the alt lengths too.
    _check(deterministic_frame(), 20, 40, 9)
    _check(real_frame(), 20, 40, 9)
