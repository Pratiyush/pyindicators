"""IndicatorSpec validation — every validator branch."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from pyindicators.core import IndicatorSpec


def _spec(**kw):
    base = dict(name="x", category="base", inputs=("close",), outputs=("x",))
    base.update(kw)
    return IndicatorSpec(**base)


def test_minimal_valid_spec_defaults():
    s = _spec()
    assert s.name == "x"
    assert s.causal is True
    assert s.talib_compatible is False
    assert s.stateful is False
    assert s.bounds == {}
    assert s.aliases == () and s.references == () and s.doc is None


def test_name_must_be_lower_snake():
    for bad in ("X", "1x", "_x", "has space", "Has-Dash"):
        with pytest.raises(ValidationError):
            _spec(name=bad)


def test_unknown_category_rejected():
    with pytest.raises(ValidationError):
        _spec(category="nope")


def test_inputs_must_be_ohlcv():
    with pytest.raises(ValidationError):
        _spec(inputs=("foo",))


def test_outputs_nonempty():
    with pytest.raises(ValidationError):
        _spec(outputs=())


def test_outputs_unique():
    with pytest.raises(ValidationError):
        _spec(outputs=("a", "a"))


def test_bounds_keys_must_be_outputs():
    with pytest.raises(ValidationError):
        _spec(outputs=("a",), bounds={"b": (0, 1)})
    s = _spec(outputs=("a",), bounds={"a": (0, 1)})
    assert s.bounds["a"] == (0.0, 1.0)


def test_spec_is_frozen():
    s = _spec()
    with pytest.raises(ValidationError):
        s.name = "y"
