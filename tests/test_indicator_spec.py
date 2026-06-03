"""Tests for the spec parser and the parametrized output-rename helper."""

from __future__ import annotations

from ohlcv_gen import deterministic_frame
from pyindicators import INDICATORS
from pyindicators.common import parse_spec, rename_outputs


def test_parse_spec_dict_form():
    assert parse_spec({"name": "sma", "params": {"period": 50}}) == ("sma", {"period": 50})
    assert parse_spec({"name": "obv"}) == ("obv", {})


def test_parse_spec_string_form_coerces_types():
    name, params = parse_spec("bbands:period=20,num_std=2.0,flag=true")
    assert name == "bbands"
    assert params == {"period": 20, "num_std": 2.0, "flag": True}
    assert isinstance(params["period"], int) and isinstance(params["num_std"], float)
    assert parse_spec("obv") == ("obv", {})


def test_rename_outputs_suffixes_by_primary_param():
    df = deterministic_frame(n=10)
    ind = INDICATORS.create("sma", period=3)
    out = rename_outputs(ind.compute(df), ind)
    assert list(out.columns) == ["sma_3"]


def test_rename_outputs_noop_without_primary_param():
    df = deterministic_frame(n=10)
    ind = INDICATORS.create("obv")  # primary_param is None
    out = rename_outputs(ind.compute(df), ind)
    assert list(out.columns) == ["obv"]
