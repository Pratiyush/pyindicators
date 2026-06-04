"""DeMarker parity — closed-form oracle on synthetic and real data.

No reference library implements DeMarker: TA-Lib, pandas-ta(_classic), finta, and ``ta`` all
lack it (TA-Lib's ``DEMA`` is the unrelated double-EMA). So instead of ``importorskip`` on a
library we pin against an *independent* closed-form reimplementation of DeMark's published
formula — built with raw pandas (rolling mean), not the library's own ``sma``/``safe_divide``.
DeMarker is a pure shift + SMA + guarded division (no smoothing seed), so parity is exact
(tight rtol/atol), checked bar-for-bar on both the synthetic walk and real market data.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS


def _oracle(df, length=14):
    """Independent DeMarker: max(H-prevH,0) and max(prevL-L,0), each SMA'd, then divided."""
    de_max = (df["high"] - df["high"].shift(1)).clip(lower=0.0)
    de_min = (df["low"].shift(1) - df["low"]).clip(lower=0.0)
    sma_max = de_max.rolling(length, min_periods=length).mean()
    sma_min = de_min.rolling(length, min_periods=length).mean()
    denom = sma_max + sma_min
    with np.errstate(divide="ignore", invalid="ignore"):
        out = sma_max / denom
    return out.mask(denom == 0, np.nan)


def _p(our, ref, *, rtol=1e-12, atol=1e-12, min_overlap=60):
    our = np.asarray(our, dtype="float64")
    ref = np.asarray(ref, dtype="float64")
    n = min(our.size, ref.size)
    our, ref = our[-n:], ref[-n:]
    mask = np.isfinite(our) & np.isfinite(ref)
    assert mask.sum() >= min_overlap
    np.testing.assert_allclose(our[mask], ref[mask], rtol=rtol, atol=atol)


def test_demarker_parity_synthetic():
    df = deterministic_frame()
    _p(INDICATORS.create("demarker", length=14).compute(df)["demarker"], _oracle(df, 14))


def test_demarker_parity_real():
    df = real_frame()
    _p(INDICATORS.create("demarker", length=14).compute(df)["demarker"], _oracle(df, 14))
