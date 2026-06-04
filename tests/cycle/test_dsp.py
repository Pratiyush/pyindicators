"""DSP (Detrended Synthetic Price) — structural / golden + edge cases."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.base import ema
from pyindicators.cycle.dsp import dsp  # noqa: F401 — import so @INDICATORS.register fires


def _series(length=14, df=None):
    df = deterministic_frame() if df is None else df
    return INDICATORS.create("dsp", length=length).compute(df)["dsp"]


def test_output_shape_and_index_preserved():
    df = deterministic_frame()
    out = INDICATORS.create("dsp").compute(df)
    assert list(out.columns) == ["dsp"]
    assert out.index.equals(df.index)
    assert out["dsp"].dtype == np.float64


def test_default_length_is_14():
    # The default length-1 warm-up NaNs (SMA seed of the EMA) confirm length defaults to 14.
    out = INDICATORS.create("dsp").compute(deterministic_frame())["dsp"]
    assert out.iloc[:13].isna().all()
    assert out.iloc[13:].notna().all()


def test_warmup_nans_match_length():
    for length in (5, 14, 30):
        out = _series(length=length)
        assert out.iloc[: length - 1].isna().all()
        assert out.iloc[length - 1 :].notna().all()


def test_equals_close_minus_ema_definition():
    # DSP is exactly close - EMA(close, length) with the TA-Lib-compatible (SMA-seeded) EMA.
    close = deterministic_frame()["close"]
    for length in (5, 14, 30):
        expected = close - ema(close, length, talib_compatible=True)
        np.testing.assert_allclose(
            _series(length=length).to_numpy(),
            expected.to_numpy(),
            rtol=0.0,
            atol=0.0,
            equal_nan=True,
        )


def test_constant_series_detrends_to_zero():
    # EMA of a constant equals the constant, so DSP collapses to 0 once seeded.
    df = frame(close=np.full(60, 42.0))
    out = INDICATORS.create("dsp", length=14).compute(df)["dsp"]
    tail = out.iloc[13:].to_numpy()
    np.testing.assert_allclose(tail, 0.0, atol=1e-9)


def test_sums_to_zero_against_ema():
    # By construction close = EMA + DSP, so adding the EMA back recovers close.
    close = deterministic_frame()["close"]
    reconstructed = ema(close, 14, talib_compatible=True) + _series(length=14)
    valid = reconstructed.notna()
    np.testing.assert_allclose(
        reconstructed[valid].to_numpy(), close[valid].to_numpy(), rtol=1e-12, atol=1e-9
    )


def test_functional_equals_registry():
    close = deterministic_frame()["close"]
    np.testing.assert_array_equal(dsp(close, 14).to_numpy(), _series(length=14).to_numpy())


def test_index_alignment_with_datetime_index():
    idx = pd.date_range("2020-01-01", periods=60, freq="D")
    df = deterministic_frame(n=60)
    df.index = idx
    out = INDICATORS.create("dsp").compute(df)
    assert out.index.equals(idx)
