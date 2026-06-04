"""EBSW — structural / golden + edge cases."""

from __future__ import annotations

import numpy as np
import pytest

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.cycle.ebsw import ebsw  # noqa: F401 — imported so @INDICATORS.register fires


def _series(length: int = 40, bars: int = 10):
    return INDICATORS.create("ebsw", length=length, bars=bars).compute(deterministic_frame())[
        "ebsw"
    ]


def test_output_shape_and_index_preserved():
    df = deterministic_frame()
    out = INDICATORS.create("ebsw").compute(df)
    assert list(out.columns) == ["ebsw"]
    assert out.index.equals(df.index)


def test_warmup_nan_then_seed_then_finite():
    out = _series()
    # First length-1 bars are NaN, index length-1 is the 0.0 seed, then finite from `length`.
    assert out.iloc[: 40 - 1].isna().all()
    assert out.iloc[40 - 1] == 0.0
    assert out.iloc[40:].notna().all()


def test_warmup_respects_length_parameter():
    out = _series(length=48, bars=10)
    assert out.iloc[: 48 - 1].isna().all()
    assert out.iloc[48 - 1] == 0.0
    assert out.iloc[48:].notna().all()


def test_bounded_in_unit_interval():
    out = _series().dropna().to_numpy()
    assert out.min() >= -1.0 - 1e-9
    assert out.max() <= 1.0 + 1e-9


def test_functional_equals_registry():
    df = deterministic_frame()
    fn = ebsw(df["close"], length=40, bars=10)
    reg = INDICATORS.create("ebsw").compute(df)["ebsw"]
    np.testing.assert_array_equal(fn.to_numpy(), reg.to_numpy())


def test_constant_series_stays_bounded():
    # A flat price still produces a non-trivial wave because the reference seeds lastClose=0,
    # so the first bar sees a full price step that decays through the SuperSmoother. The output
    # must merely stay inside the [-1, 1] envelope (a degenerate input, but faithful to the ref).
    df = deterministic_frame().assign(close=100.0)
    out = INDICATORS.create("ebsw").compute(df)["ebsw"].dropna().to_numpy()
    assert out.min() >= -1.0 - 1e-9
    assert out.max() <= 1.0 + 1e-9


def test_golden_seed_value_is_zero():
    # Tiny frame: only the warm-up seed (index length-1) exists, and it must be exactly 0.0.
    df = frame([100.0 + i for i in range(45)])
    out = INDICATORS.create("ebsw").compute(df)["ebsw"]
    assert out.iloc[39] == 0.0
    assert out.iloc[:39].isna().all()


def test_oscillator_actually_oscillates():
    # A genuine cyclic input should drive the wave across both signs (it is a sinewave).
    n = 400
    close = 100.0 + 5.0 * np.sin(np.arange(n) * 2.0 * np.pi / 20.0)
    df = frame(close)
    out = INDICATORS.create("ebsw").compute(df)["ebsw"].dropna().to_numpy()
    assert out.min() < -0.1
    assert out.max() > 0.1


def test_length_below_minimum_rejected():
    with pytest.raises(ValueError):
        INDICATORS.create("ebsw", length=38)


def test_bars_below_minimum_rejected():
    with pytest.raises(ValueError):
        INDICATORS.create("ebsw", bars=0)


def test_unknown_param_rejected():
    with pytest.raises(ValueError):
        INDICATORS.create("ebsw", drift=1)
