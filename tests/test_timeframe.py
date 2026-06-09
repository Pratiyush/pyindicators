"""Tests for the canonical Timeframe enum (S1.1).

The token map pins the exact string values so they stay in lock-step with the
downstream app's ``core/types.py:Timeframe`` (re-export target).
"""

import pytest

from pyindicators import Timeframe

ALL = list(Timeframe)
INTRADAY = {Timeframe.HOUR, Timeframe.MIN15, Timeframe.MIN5, Timeframe.MIN1}
TOKENS = {
    Timeframe.MONTH: "1mo",
    Timeframe.WEEK: "1wk",
    Timeframe.DAY: "1d",
    Timeframe.HOUR: "1h",
    Timeframe.MIN15: "15m",
    Timeframe.MIN5: "5m",
    Timeframe.MIN1: "1m",
}
RULES = {
    Timeframe.MONTH: "MS",
    Timeframe.WEEK: "W-FRI",
    Timeframe.DAY: "1D",
    Timeframe.HOUR: "1h",
    Timeframe.MIN15: "15min",
    Timeframe.MIN5: "5min",
    Timeframe.MIN1: "1min",
}

_IDS = [t.name for t in ALL]


@pytest.mark.parametrize("tf", ALL, ids=_IDS)
def test_timeframe_from_str_all_members(tf):
    assert Timeframe(tf.value) is tf


@pytest.mark.parametrize("tf", ALL, ids=_IDS)
def test_is_intraday_per_member(tf):
    assert tf.is_intraday is (tf in INTRADAY)


@pytest.mark.parametrize("tf", ALL, ids=_IDS)
def test_pandas_rule_per_member(tf):
    assert tf.pandas_rule == RULES[tf]


@pytest.mark.parametrize("tf", ALL, ids=_IDS)
def test_str_equality_holds(tf):
    assert tf == TOKENS[tf]
    assert tf.value == TOKENS[tf]


def test_invalid_token_raises():
    with pytest.raises(ValueError):
        Timeframe("3d")
