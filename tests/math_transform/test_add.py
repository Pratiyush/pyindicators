"""ADD (high + low) — golden + edge cases."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.math_transform.add import add  # noqa: F401 - import fires @register


def test_add_is_elementwise_sum():
    # Literal element-wise sum of the high and low series, bar by bar (no warm-up).
    df = frame([0.0, 0.0, 0.0], high=[1.0, 2.0, 3.0], low=[10.0, 20.0, 30.0])
    out = INDICATORS.create("add").compute(df)["add"]
    np.testing.assert_allclose(out.to_numpy(), [11.0, 22.0, 33.0], atol=1e-12)


def test_add_no_warmup_full_length():
    # Parameter-free pointwise op: output length == input length, every bar finite here.
    df = deterministic_frame(200)
    out = INDICATORS.create("add").compute(df)["add"]
    assert len(out) == len(df)
    assert out.notna().all()
    np.testing.assert_allclose(
        out.to_numpy(),
        df["high"].to_numpy(dtype="float64") + df["low"].to_numpy(dtype="float64"),
        atol=1e-12,
    )


def test_add_nan_propagates():
    # NaN in either operand -> NaN at that bar (undefined sum, not fabricated).
    df = frame([0.0, 0.0, 0.0], high=[1.0, np.nan, 3.0], low=[10.0, 20.0, np.nan])
    out = INDICATORS.create("add").compute(df)["add"]
    assert out.iloc[0] == 11.0
    assert np.isnan(out.iloc[1])
    assert np.isnan(out.iloc[2])


def test_add_output_is_float64():
    df = deterministic_frame(50)
    out = INDICATORS.create("add").compute(df)
    assert list(out.columns) == ["add"]
    assert out["add"].dtype == np.float64
