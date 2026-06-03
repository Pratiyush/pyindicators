"""Registry behaviour."""

from __future__ import annotations

import pytest

from pyindicators import INDICATORS
from pyindicators.core import Indicator, IndicatorSpec, Registry


def _make(name):
    class _Ind(Indicator):
        spec = IndicatorSpec(name=name, category="base", inputs=("close",), outputs=("o",))

        def _compute(self, df):
            return df["close"]

    return _Ind


def test_global_registry_has_base_indicators():
    assert "sma" in INDICATORS and len(INDICATORS) >= 7
    assert INDICATORS.get("sma").spec.name == "sma"
    assert "definitely_not_registered" not in INDICATORS


def test_register_get_create_names_all_iter_len():
    reg = Registry("widget")
    cls = reg.register(_make("foo"))
    assert "foo" in reg and len(reg) == 1
    assert reg.names() == ["foo"]
    assert reg.all() == {"foo": cls}
    assert list(reg) == [cls]
    assert isinstance(reg.create("foo"), cls)


def test_duplicate_registration_raises():
    reg = Registry()
    reg.register(_make("dup"))
    with pytest.raises(ValueError):
        reg.register(_make("dup"))


def test_get_unknown_raises_keyerror():
    with pytest.raises(KeyError):
        Registry().get("missing")
