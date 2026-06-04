"""STDERR parity vs a pandas-ta-backed closed form — synthetic and real data.

pandas-ta's ``stderr`` is a *different* quantity (``stdev(close)/sqrt(length)`` — the standard
error of the mean), so it is not a valid oracle for the regression standard error. Instead we
cross-check against the exact identity built on a reference library's stdev:

    stderr_regression = stdev(close, ddof=1) * sqrt( (1 - r^2) * (length-1) / (length-2) )

where ``r`` is the Pearson correlation of the window with a time ramp. Both sides are
non-recursive (no Wilder/EMA seeding), so a tight rtol holds over the whole finite overlap.
"""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS
from pyindicators.statistics.stderr import stderr  # import so @register fires

pta = pytest.importorskip("pandas_ta_classic")


def _oracle(close, length: int) -> np.ndarray:
    """Reference: pandas-ta ``stdev`` (ddof=1) scaled by the r^2 / dof identity."""
    sd = pta.stdev(close, length=length, ddof=1).to_numpy()  # sqrt(Syy / (length-1))
    x = np.arange(length, dtype="float64")
    c = np.asarray(close, dtype="float64")
    out = np.full(c.size, np.nan)
    for i in range(length - 1, c.size):
        w = c[i - length + 1 : i + 1]
        if np.ptp(w) == 0.0:  # flat window: r undefined, but residuals are exactly 0
            out[i] = 0.0
            continue
        r = float(np.corrcoef(x, w)[0, 1])
        out[i] = sd[i] * np.sqrt((1.0 - r * r) * (length - 1) / (length - 2))
    return out


def _p(our, ref, *, rtol=1e-7, atol=1e-9, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_stderr_parity_synthetic():
    df = deterministic_frame()
    out = INDICATORS.create("stderr", length=14).compute(df)["stderr"]
    # the registry path and the imported functional API are identical (pins the @register import)
    np.testing.assert_allclose(out.to_numpy(), stderr(df["close"], 14).to_numpy(), atol=0.0)
    _p(out, _oracle(df["close"], 14))


def test_stderr_parity_real():
    df = real_frame()
    out = INDICATORS.create("stderr", length=14).compute(df)["stderr"]
    _p(out, _oracle(df["close"], 14))
