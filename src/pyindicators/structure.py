"""Support/resistance structure: rolling extremes, Donchian channel, distance-from-extreme.

Trailing-window primitives used by breakout/52-week-high screens (Donchian; Minervini's
within-25%-of-high / 30%-above-low gates). All trailing-only (causal).
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from .base import Indicator
from .common import build_output, require_columns
from .registry import INDICATORS


class _Window(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    window: int = Field(default=252, ge=1)


@INDICATORS.register("rolling_high")
class RollingHigh(Indicator):
    """Trailing maximum of high over ``window`` bars (e.g. 252 = ~52-week high)."""

    name = "rolling_high"
    outputs = ("rolling_high",)
    primary_param = "window"
    params_model = _Window

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("high",))
        w = self.params["window"]
        return build_output(
            df.index, {"rolling_high": df["high"].rolling(w, min_periods=w).max()}
        )


@INDICATORS.register("rolling_low")
class RollingLow(Indicator):
    """Trailing minimum of low over ``window`` bars (e.g. 252 = ~52-week low)."""

    name = "rolling_low"
    outputs = ("rolling_low",)
    primary_param = "window"
    params_model = _Window

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("low",))
        w = self.params["window"]
        return build_output(
            df.index, {"rolling_low": df["low"].rolling(w, min_periods=w).min()}
        )


@INDICATORS.register("donchian")
class Donchian(Indicator):
    """Donchian channel: trailing high/low/mid over ``window`` bars."""

    name = "donchian"
    outputs = ("dc_upper", "dc_lower", "dc_mid")
    primary_param = "window"

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        window: int = Field(default=20, ge=1)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("high", "low"))
        w = self.params["window"]
        upper = df["high"].rolling(w, min_periods=w).max()
        lower = df["low"].rolling(w, min_periods=w).min()
        return build_output(
            df.index, {"dc_upper": upper, "dc_lower": lower, "dc_mid": (upper + lower) / 2.0}
        )


@INDICATORS.register("pct_from_high")
class PctFromHigh(Indicator):
    """Fractional distance below the trailing high: ``close / rolling_high - 1`` (<= 0)."""

    name = "pct_from_high"
    outputs = ("pct_from_high",)
    primary_param = "window"
    params_model = _Window

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("high", "close"))
        w = self.params["window"]
        hh = df["high"].rolling(w, min_periods=w).max()
        return build_output(df.index, {"pct_from_high": df["close"] / hh - 1.0})


@INDICATORS.register("pct_from_low")
class PctFromLow(Indicator):
    """Fractional distance above the trailing low: ``close / rolling_low - 1`` (>= 0)."""

    name = "pct_from_low"
    outputs = ("pct_from_low",)
    primary_param = "window"
    params_model = _Window

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("low", "close"))
        w = self.params["window"]
        ll = df["low"].rolling(w, min_periods=w).min()
        return build_output(df.index, {"pct_from_low": df["close"] / ll - 1.0})
