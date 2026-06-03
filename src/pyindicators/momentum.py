"""Momentum oscillators: RSI, ROC, Momentum, Stochastic, CCI, Williams %R.

Canonical definitions: RSI (Wilder 1978), Stochastic (Lane), CCI (Lambert 1980),
Williams %R (Williams). All trailing-only (causal).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from .base import Indicator
from .common import build_output, require_columns, typical_price, wilder_rma
from .registry import INDICATORS


@INDICATORS.register("rsi")
class RSI(Indicator):
    """Wilder's Relative Strength Index, bounded [0, 100]."""

    name = "rsi"
    outputs = ("rsi",)
    primary_param = "period"
    bounds = {"rsi": (0.0, 100.0)}

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=14, ge=1)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("close",))
        p = self.params["period"]
        delta = df["close"].diff()
        gain = delta.clip(lower=0.0)
        loss = -delta.clip(upper=0.0)
        avg_gain = wilder_rma(gain, p)
        avg_loss = wilder_rma(loss, p)
        with np.errstate(divide="ignore", invalid="ignore"):
            rs = avg_gain / avg_loss          # pure gains => inf => rsi 100
            rsi = 100.0 - 100.0 / (1.0 + rs)  # pure losses => rs 0 => rsi 0
        # A flat window (no gains AND no losses) is undefined -> NaN, not 100.
        rsi = rsi.mask((avg_gain == 0) & (avg_loss == 0))
        return build_output(df.index, {"rsi": rsi})


@INDICATORS.register("roc")
class ROC(Indicator):
    """Rate of change: percent change over ``period`` bars."""

    name = "roc"
    outputs = ("roc",)
    primary_param = "period"

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=12, ge=1)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("close",))
        p = self.params["period"]
        roc = (df["close"] / df["close"].shift(p) - 1.0) * 100.0
        return build_output(df.index, {"roc": roc})


@INDICATORS.register("momentum")
class Momentum(Indicator):
    """Absolute price momentum: ``close - close.shift(period)``."""

    name = "momentum"
    outputs = ("mom",)
    primary_param = "period"

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=10, ge=1)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("close",))
        p = self.params["period"]
        return build_output(df.index, {"mom": df["close"] - df["close"].shift(p)})


@INDICATORS.register("stoch")
class Stochastic(Indicator):
    """Stochastic oscillator %K/%D (Lane), bounded [0, 100]."""

    name = "stoch"
    outputs = ("stoch_k", "stoch_d")
    primary_param = "k"
    bounds = {"stoch_k": (0.0, 100.0), "stoch_d": (0.0, 100.0)}

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        k: int = Field(default=14, ge=1)
        d: int = Field(default=3, ge=1)
        smooth_k: int = Field(default=3, ge=1)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("high", "low", "close"))
        k, d, sk = self.params["k"], self.params["d"], self.params["smooth_k"]
        ll = df["low"].rolling(k, min_periods=k).min()
        hh = df["high"].rolling(k, min_periods=k).max()
        raw_k = 100.0 * (df["close"] - ll) / (hh - ll)
        stoch_k = raw_k.rolling(sk, min_periods=sk).mean()
        stoch_d = stoch_k.rolling(d, min_periods=d).mean()
        return build_output(df.index, {"stoch_k": stoch_k, "stoch_d": stoch_d})


@INDICATORS.register("cci")
class CCI(Indicator):
    """Commodity Channel Index (Lambert)."""

    name = "cci"
    outputs = ("cci",)
    primary_param = "period"

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=20, ge=1)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("high", "low", "close"))
        p = self.params["period"]
        tp = typical_price(df)
        sma_tp = tp.rolling(p, min_periods=p).mean()
        mad = tp.rolling(p, min_periods=p).apply(
            lambda x: np.abs(x - x.mean()).mean(), raw=True
        )
        cci = (tp - sma_tp) / (0.015 * mad)
        return build_output(df.index, {"cci": cci})


@INDICATORS.register("willr")
class WilliamsR(Indicator):
    """Williams %R, bounded [-100, 0]."""

    name = "willr"
    outputs = ("willr",)
    primary_param = "period"
    bounds = {"willr": (-100.0, 0.0)}

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=14, ge=1)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("high", "low", "close"))
        p = self.params["period"]
        hh = df["high"].rolling(p, min_periods=p).max()
        ll = df["low"].rolling(p, min_periods=p).min()
        willr = -100.0 * (hh - df["close"]) / (hh - ll)
        return build_output(df.index, {"willr": willr})
