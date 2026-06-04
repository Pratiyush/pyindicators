"""BRAR (AR & BR) — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS


def test_brar_positive_and_finite():
    out = INDICATORS.create("brar", length=26).compute(deterministic_frame(200))
    for col in ("ar", "br"):
        v = out[col].dropna().to_numpy()
        assert v.size > 100 and (v >= 0).all() and np.isfinite(v).all()


def test_brar_ar_100_when_symmetric():
    # open midway between high and low every bar -> sum(H-O) == sum(O-L) -> AR == 100
    n = 40
    high = np.full(n, 11.0)
    low = np.full(n, 9.0)
    open_ = np.full(n, 10.0)
    out = INDICATORS.create("brar", length=10).compute(
        frame(open_, high=high, low=low, open_=open_)
    )["ar"]
    np.testing.assert_allclose(out.dropna().to_numpy(), 100.0)


def test_brar_short_frame_all_nan():
    out = INDICATORS.create("brar", length=26).compute(frame([1.0, 2.0, 3.0]))
    assert out["ar"].isna().all() and out["br"].isna().all()
