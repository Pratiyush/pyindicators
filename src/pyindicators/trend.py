"""Trend indicators: moving averages, slope, MACD, ADX, Aroon.

Canonical definitions: moving averages (Murphy, *Technical Analysis of the Financial
Markets*), MACD (Appel 1979), ADX/DMI (Wilder 1978), Aroon (Chande 1995). All are
trailing-only (causal) and vectorized.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .base import Indicator
from .common import build_output, ema, require_columns, true_range, wilder_rma
from .registry import INDICATORS


class _Period(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    period: int = Field(default=50, ge=1)


@INDICATORS.register("sma")
class SMA(Indicator):
    """Simple moving average of close."""

    name = "sma"
    outputs = ("sma",)
    primary_param = "period"

    class Params(_Period):
        period: int = Field(default=50, ge=1)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("close",))
        p = self.params["period"]
        return build_output(df.index, {"sma": df["close"].rolling(p, min_periods=p).mean()})


@INDICATORS.register("ema")
class EMA(Indicator):
    """Exponential moving average of close (``adjust=False``)."""

    name = "ema"
    outputs = ("ema",)
    primary_param = "period"

    class Params(_Period):
        period: int = Field(default=20, ge=1)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("close",))
        return build_output(df.index, {"ema": ema(df["close"], self.params["period"])})


@INDICATORS.register("wma")
class WMA(Indicator):
    """Linearly weighted moving average (weights 1..period, most recent heaviest)."""

    name = "wma"
    outputs = ("wma",)
    primary_param = "period"

    class Params(_Period):
        period: int = Field(default=20, ge=1)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("close",))
        p = self.params["period"]
        weights = np.arange(1, p + 1, dtype="float64")
        wma = df["close"].rolling(p, min_periods=p).apply(
            lambda x: np.dot(x, weights) / weights.sum(), raw=True
        )
        return build_output(df.index, {"wma": wma})


@INDICATORS.register("sma_slope")
class SMASlope(Indicator):
    """Per-bar slope of an SMA: ``(sma - sma.shift(lookback)) / lookback``.

    Used by Minervini/Weinstein "the 200-day MA is rising" checks (slope > 0).
    """

    name = "sma_slope"
    outputs = ("sma_slope",)
    primary_param = "period"

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=200, ge=1)
        lookback: int = Field(default=22, ge=1)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("close",))
        p, lb = self.params["period"], self.params["lookback"]
        sma = df["close"].rolling(p, min_periods=p).mean()
        slope = (sma - sma.shift(lb)) / lb
        return build_output(df.index, {"sma_slope": slope})


@INDICATORS.register("macd")
class MACD(Indicator):
    """Moving Average Convergence/Divergence (Appel)."""

    name = "macd"
    outputs = ("macd", "macd_signal", "macd_hist")

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        fast: int = Field(default=12, ge=1)
        slow: int = Field(default=26, ge=1)
        signal: int = Field(default=9, ge=1)

        @model_validator(mode="after")
        def _check(self):
            if self.fast >= self.slow:
                raise ValueError("macd requires fast < slow")
            return self

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("close",))
        fast, slow, sig = self.params["fast"], self.params["slow"], self.params["signal"]
        # MACD is conventionally defined from the start (no min_periods warm-up).
        macd = (
            df["close"].ewm(span=fast, adjust=False).mean()
            - df["close"].ewm(span=slow, adjust=False).mean()
        )
        signal = macd.ewm(span=sig, adjust=False).mean()
        return build_output(
            df.index,
            {"macd": macd, "macd_signal": signal, "macd_hist": macd - signal},
        )


@INDICATORS.register("adx")
class ADX(Indicator):
    """Average Directional Index + directional indicators (Wilder DMI)."""

    name = "adx"
    outputs = ("adx", "plus_di", "minus_di")
    primary_param = "period"
    bounds = {"adx": (0.0, 100.0), "plus_di": (0.0, 100.0), "minus_di": (0.0, 100.0)}

    class Params(_Period):
        period: int = Field(default=14, ge=1)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("high", "low", "close"))
        p = self.params["period"]
        up = df["high"].diff()
        down = -df["low"].diff()
        plus_dm = np.where((up > down) & (up > 0), up, 0.0)
        minus_dm = np.where((down > up) & (down > 0), down, 0.0)
        plus_dm = pd.Series(plus_dm, index=df.index)
        minus_dm = pd.Series(minus_dm, index=df.index)
        atr = wilder_rma(true_range(df), p)
        plus_di = 100.0 * wilder_rma(plus_dm, p) / atr
        minus_di = 100.0 * wilder_rma(minus_dm, p) / atr
        dx = 100.0 * (plus_di - minus_di).abs() / (plus_di + minus_di)
        adx = wilder_rma(dx, p)
        return build_output(
            df.index, {"adx": adx, "plus_di": plus_di, "minus_di": minus_di}
        )


@INDICATORS.register("aroon")
class Aroon(Indicator):
    """Aroon Up/Down: how recently the rolling high/low occurred (Chande)."""

    name = "aroon"
    outputs = ("aroon_up", "aroon_down")
    primary_param = "period"
    bounds = {"aroon_up": (0.0, 100.0), "aroon_down": (0.0, 100.0)}

    class Params(_Period):
        period: int = Field(default=25, ge=1)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("high", "low"))
        p = self.params["period"]
        win = p + 1  # window includes the current bar
        up = df["high"].rolling(win, min_periods=win).apply(
            lambda x: 100.0 * x.argmax() / p, raw=True
        )
        down = df["low"].rolling(win, min_periods=win).apply(
            lambda x: 100.0 * x.argmin() / p, raw=True
        )
        return build_output(df.index, {"aroon_up": up, "aroon_down": down})
