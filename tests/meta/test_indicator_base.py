"""The Indicator base class: input validation, output coercion, params, cache_key.

Dummy indicators below are intentionally NOT registered (no decorator), so they don't
pollute the global registry / meta-tests.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pyindicators import INDICATORS
from pyindicators.core import Indicator, IndicatorSpec


def _df(n=6):
    c = np.arange(1.0, n + 1)
    return pd.DataFrame(
        {"open": c, "high": c + 0.5, "low": c - 0.5, "close": c, "volume": np.ones(n)}
    )


class DictOut(Indicator):
    spec = IndicatorSpec(name="dummy_dict", category="base", inputs=("close",), outputs=("a", "b"))

    def _compute(self, df):
        return {"a": df["close"], "b": df["close"] * 2}


class FrameOut(Indicator):
    spec = IndicatorSpec(name="dummy_frame", category="base", inputs=("close",), outputs=("x",))

    def _compute(self, df):
        return pd.DataFrame({"x": df["close"]})


class ArrayOut(Indicator):
    spec = IndicatorSpec(name="dummy_array", category="base", inputs=("close",), outputs=("x",))

    def _compute(self, df):
        return {"x": df["close"].to_numpy()}  # non-Series value -> coerced by _finalize


class MissingOut(Indicator):
    spec = IndicatorSpec(
        name="dummy_missing", category="base", inputs=("close",), outputs=("x", "y")
    )

    def _compute(self, df):
        return {"x": df["close"]}  # 'y' missing


class NoParams(Indicator):
    spec = IndicatorSpec(name="dummy_noparams", category="base", inputs=("close",), outputs=("x",))

    def _compute(self, df):
        return df["close"]


def test_dict_output():
    out = DictOut().compute(_df())
    assert list(out.columns) == ["a", "b"]
    assert (out["b"] == out["a"] * 2).all()


def test_frame_output():
    assert list(FrameOut().compute(_df()).columns) == ["x"]


def test_array_value_is_coerced_to_float_series():
    out = ArrayOut().compute(_df())
    assert list(out.columns) == ["x"] and str(out["x"].dtype) == "float64"


def test_missing_output_raises():
    with pytest.raises(ValueError):
        MissingOut().compute(_df())


def test_require_inputs_raises_on_missing_column():
    with pytest.raises(ValueError):
        NoParams().compute(pd.DataFrame({"high": [1.0]}))


def test_no_params_indicator_rejects_params():
    with pytest.raises(TypeError):
        NoParams(length=5)


def test_outputs_property():
    assert NoParams().outputs == ("x",)


def test_cache_key_is_param_sensitive():
    a = INDICATORS.create("sma", length=10).cache_key()
    b = INDICATORS.create("sma", length=20).cache_key()
    assert a != b and a.startswith("sma-")
