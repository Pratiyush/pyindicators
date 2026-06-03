"""Registry + Timeframe contracts."""

from __future__ import annotations

import pytest

from pyindicators import INDICATORS, Registry, Timeframe


def test_registry_register_get_create_contains_len():
    reg: Registry = Registry("widget")

    @reg.register("foo")
    class Foo:
        def __init__(self, x=1):
            self.x = x

    assert "foo" in reg and "FOO" in reg and len(reg) == 1
    assert reg.names() == ["foo"] and reg.all() == {"foo": Foo}
    assert reg.get("foo") is Foo and reg.create("foo", x=3).x == 3


def test_registry_duplicate_override_and_unknown():
    reg: Registry = Registry("widget")

    @reg.register("a")
    class A:
        pass

    with pytest.raises(ValueError):
        @reg.register("a")
        class B:
            pass

    @reg.register("a", override=True)
    class C:
        pass

    assert reg.get("a") is C
    with pytest.raises(KeyError):
        reg.get("missing")


def test_timeframe_rules_and_intraday():
    for tf in Timeframe:
        assert isinstance(tf.pandas_rule, str) and tf.pandas_rule
    assert Timeframe.HOUR.is_intraday and Timeframe.MIN1.is_intraday
    assert not Timeframe.DAY.is_intraday and not Timeframe.WEEK.is_intraday
    assert Timeframe.DAY.value == "1d"


def test_indicators_registry_is_populated():
    assert "sma" in INDICATORS and "rsi" in INDICATORS and len(INDICATORS) >= 38
