"""Shared candle geometry + TA-Lib ``CandleSettings`` averaging — the candle foundation.

Every ``CDL*`` pattern in TA-Lib sizes a bar's body/shadows relative to a rolling average
defined by a *CandleSetting* ``(RangeType, AvgPeriod, Factor)``. This module reproduces that
machinery **bit-exactly** so any pattern composed on top matches ``talib.CDL*`` with no
tolerance (candles are integer -100/0/100 outputs).

Two pieces:

* geometry per bar — :func:`real_body`, :func:`upper_shadow`, :func:`lower_shadow`,
  :func:`hl_range`, :func:`candle_color` (+1 white / -1 black).
* :func:`candle_average` — the per-bar threshold ``Series`` for any of the 11 settings,
  i.e. the right-hand side TA-Lib compares a body/shadow against.

The exact ``TA_CANDLEAVERAGE`` formula (reverse-engineered and verified against ``talib`` on
both ``deterministic_frame()`` and real AAPL daily bars)::

    avg(i) = Factor * ( AvgPeriod == 0
                          ? rangeType(i)                       # current bar only
                          : sum(rangeType[i-AvgPeriod .. i-1]) / AvgPeriod )
             / (RangeType == Shadows ? 2.0 : 1.0)

i.e. when ``AvgPeriod > 0`` the window is the ``AvgPeriod`` bars **ending at ``i-1``**
(EXCLUSIVE of the current bar ``i``); bars before the window is full are ``NaN`` (TA-Lib
emits 0 there — its lookback equals the setting's ``AvgPeriod``).

IMPORTANT — verified RangeTypes that differ from some published default tables (this is the
subtle bug that breaks naive ports): ``BodyDoji`` and ``ShadowVeryShort`` both use
**HighLow** (not RealBody / Shadows). See :data:`CANDLE_SETTINGS`.

No ``@register`` here — this is a pure helper module reused by every pattern.
"""

from __future__ import annotations

from typing import NamedTuple

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, LOW, OPEN

# --- RangeType identifiers (mirror TA-Lib's TA_RangeType enum) -------------------------
REAL_BODY = "RealBody"
HIGH_LOW = "HighLow"
SHADOWS = "Shadows"


class CandleSetting(NamedTuple):
    """One TA-Lib CandleSetting: a range type, an averaging period, and a scale factor."""

    range_type: str
    avg_period: int
    factor: float


#: The 11 TA-Lib CandleSettings, with RangeTypes verified bit-exactly against ``talib``.
#:
#: ``BodyDoji`` and ``ShadowVeryShort`` use ``HighLow`` (empirically confirmed via CDLDOJI,
#: CDLMARUBOZU, CDLCLOSINGMARUBOZU, CDLGRAVESTONEDOJI). ``Near``/``Far`` keep TA-Lib's
#: documented ``HighLow`` family (consistent with the confirmed ``Equal`` = HighLow); they
#: are not exercised by patterns present in the fixtures, so they are not independently
#: nailed here — verify them when a Near/Far pattern is added.
CANDLE_SETTINGS: dict[str, CandleSetting] = {
    "BodyLong": CandleSetting(REAL_BODY, 10, 1.0),
    "BodyVeryLong": CandleSetting(REAL_BODY, 10, 3.0),
    "BodyShort": CandleSetting(REAL_BODY, 10, 1.0),
    "BodyDoji": CandleSetting(HIGH_LOW, 10, 0.1),
    "ShadowLong": CandleSetting(REAL_BODY, 0, 1.0),
    "ShadowVeryLong": CandleSetting(REAL_BODY, 0, 2.0),
    "ShadowShort": CandleSetting(SHADOWS, 10, 1.0),
    "ShadowVeryShort": CandleSetting(HIGH_LOW, 10, 0.1),
    "Near": CandleSetting(HIGH_LOW, 5, 0.2),
    "Far": CandleSetting(HIGH_LOW, 5, 0.6),
    "Equal": CandleSetting(HIGH_LOW, 5, 0.05),
}


# --- per-bar geometry ------------------------------------------------------------------
def real_body(df: pd.DataFrame) -> pd.Series:
    """``abs(close - open)`` — the candle's body length."""
    return (df[CLOSE] - df[OPEN]).abs()


def hl_range(df: pd.DataFrame) -> pd.Series:
    """``high - low`` — the candle's full range."""
    return df[HIGH] - df[LOW]


def upper_shadow(df: pd.DataFrame) -> pd.Series:
    """``high - max(open, close)`` — the upper wick."""
    return df[HIGH] - df[[OPEN, CLOSE]].max(axis=1)


def lower_shadow(df: pd.DataFrame) -> pd.Series:
    """``min(open, close) - low`` — the lower wick."""
    return df[[OPEN, CLOSE]].min(axis=1) - df[LOW]


def both_shadows(df: pd.DataFrame) -> pd.Series:
    """``upper_shadow + lower_shadow`` — the ``Shadows`` range type."""
    return upper_shadow(df) + lower_shadow(df)


def candle_color(df: pd.DataFrame) -> pd.Series:
    """+1 for a white candle (``close >= open``), -1 for a black candle.

    Matches TA-Lib's ``TA_CANDLECOLOR`` (a doji with ``close == open`` is treated as white).
    Returned as int64.
    """
    return pd.Series(np.where(df[CLOSE].to_numpy() >= df[OPEN].to_numpy(), 1, -1), index=df.index)


def _range_series(df: pd.DataFrame, range_type: str) -> pd.Series:
    if range_type == REAL_BODY:
        return real_body(df)
    if range_type == HIGH_LOW:
        return hl_range(df)
    if range_type == SHADOWS:
        return both_shadows(df)
    raise ValueError(f"unknown range type {range_type!r}; expected one of "
                     f"{REAL_BODY!r}, {HIGH_LOW!r}, {SHADOWS!r}")


def candle_average(df: pd.DataFrame, setting_name: str) -> pd.Series:
    """Per-bar TA-Lib ``CandleSetting`` threshold for ``setting_name``.

    Returns the ``Series`` that a body/shadow is compared against in a ``CDL*`` pattern,
    bit-exactly matching ``TA_CANDLEAVERAGE`` (see the module docstring for the formula).

    For ``AvgPeriod > 0`` the average is over the ``AvgPeriod`` bars **ending at ``i-1``**
    (the current bar is excluded); the first ``AvgPeriod`` bars are ``NaN``. For
    ``AvgPeriod == 0`` the "average" is just the current bar's range (no warm-up).
    """
    if setting_name not in CANDLE_SETTINGS:
        raise KeyError(
            f"unknown candle setting {setting_name!r}; known: {sorted(CANDLE_SETTINGS)}"
        )
    setting = CANDLE_SETTINGS[setting_name]
    rng = _range_series(df, setting.range_type)
    divisor = 2.0 if setting.range_type == SHADOWS else 1.0

    if setting.avg_period == 0:
        avg = rng
    else:
        # Trailing mean over the AvgPeriod bars ending at i-1: shift out the current bar,
        # then a closed rolling mean that requires a full window (NaN until it fills).
        prev = rng.shift(1)
        avg = prev.rolling(window=setting.avg_period, min_periods=setting.avg_period).mean()

    return setting.factor * avg / divisor
