"""Tests for the feature-assembly layer (S1.2): parse_spec, naming, build_features."""

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS, build_features, parse_spec
from pyindicators.features import _coerce, build_output, primary_param, rename_outputs


@pytest.fixture(scope="module")
def df():
    return deterministic_frame()


# --- _coerce -------------------------------------------------------------------
@pytest.mark.parametrize(
    "raw,expected",
    [("50", 50), ("2.0", 2.0), ("true", True), ("false", False), ("bar", "bar")],
)
def test_coerce(raw, expected):
    got = _coerce(raw)
    assert got == expected and type(got) is type(expected)


# --- parse_spec ----------------------------------------------------------------
def test_parse_string_with_params():
    assert parse_spec("sma:length=50") == ("sma", {"length": 50})


def test_parse_string_multi_params():
    assert parse_spec("bbands:length=20,mult=2.0") == ("bbands", {"length": 20, "mult": 2.0})


def test_parse_string_no_params():
    assert parse_spec("macd") == ("macd", {})


def test_parse_dict_form():
    assert parse_spec({"name": "sma", "params": {"length": 50}}) == ("sma", {"length": 50})


def test_parse_dict_no_params():
    assert parse_spec({"name": "obv"}) == ("obv", {})


# --- build_output --------------------------------------------------------------
def test_build_output_series_and_array():
    idx = pd.RangeIndex(3)
    out = build_output(idx, {"a": pd.Series([1, 2, 3], index=idx), "b": np.array([4, 5, 6])})
    assert list(out.columns) == ["a", "b"]
    assert str(out["a"].dtype) == "float64"
    assert out["b"].tolist() == [4.0, 5.0, 6.0]


# --- primary_param / rename_outputs --------------------------------------------
def test_primary_param_length():
    assert primary_param(INDICATORS.create("sma", length=50)) == "length"


def test_primary_param_skips_flag():
    # ema params are (length, talib_compatible); the flag is skipped, length wins.
    assert primary_param(INDICATORS.create("ema", length=13)) == "length"


def test_primary_param_none_for_paramless():
    assert primary_param(INDICATORS.create("obv")) is None


def test_rename_outputs_suffixes(df):
    ind = INDICATORS.create("sma", length=50)
    assert list(rename_outputs(ind.compute(df), ind).columns) == ["sma_50"]


def test_rename_outputs_static_when_no_primary(df):
    ind = INDICATORS.create("obv")
    assert list(rename_outputs(ind.compute(df), ind).columns) == ["obv"]


# --- build_features ------------------------------------------------------------
def test_build_features_multi_spec(df):
    out = build_features(df, ["sma:length=50", "sma:length=150", "rsi:length=14"])
    for col in ("sma_50", "sma_150", "rsi_14"):
        assert col in out.columns and str(out[col].dtype) == "float64"
    assert out.index.equals(df.index)
    assert not df.columns.str.startswith("sma_").any()  # df not mutated


def test_build_features_dedupes(df):
    out = build_features(df, ["sma:length=50", {"name": "sma", "params": {"length": 50}}])
    assert (out.columns == "sma_50").sum() == 1


def test_build_features_collision_raises(df):
    with pytest.raises(ValueError, match="collision"):
        build_features(df, ["bbands:length=20,mult=2.0", "bbands:length=20,mult=2.5"])


def test_build_features_multi_output_suffixed(df):
    # macd's first scalar param is ``fast``=12, so every output column is suffixed with 12.
    out = build_features(df, ["macd"])
    assert {"macd_12", "macd_signal_12", "macd_hist_12"} <= set(out.columns)


# --- the 302 sweep: every indicator is reachable + collision-free --------------
@pytest.mark.parametrize("name", INDICATORS.names(), ids=INDICATORS.names())
def test_build_features_every_indicator(df, name):
    out = build_features(df, [{"name": name}])
    ind = INDICATORS.create(name)
    expected = list(rename_outputs(ind.compute(df), ind).columns)
    assert expected, name
    for col in expected:
        assert col in out.columns
        assert str(out[col].dtype) == "float64"
    assert out.index.equals(df.index)


# --- build_features benchmark injection (S1.4) ---------------------------------
def test_build_features_benchmark_injected(df):
    bench = df["close"] * 1.01
    out = build_features(df, ["rs_line"], benchmark_close=bench)
    assert "rs_line" in out.columns
    np.testing.assert_allclose(
        out["rs_line"].to_numpy(), (df["close"] / bench).to_numpy()
    )


def test_build_features_benchmark_length_mismatch_raises(df):
    with pytest.raises(ValueError, match="length"):
        build_features(df, ["rs_line"], benchmark_close=[1.0, 2.0])
