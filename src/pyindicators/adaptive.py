"""Adaptive / advanced trend indicators: KAMA, Hull MA, Vortex.

Sources: Kaufman Adaptive Moving Average (Perry Kaufman); Hull Moving Average
(Alan Hull, 2005); Vortex Indicator (Botes & Siepman, 2010). All trailing-only (causal).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .base import Indicator
from .common import build_output, require_columns, true_range
from .registry import INDICATORS


def _wma(s: pd.Series, length: int) -> pd.Series:
    weights = np.arange(1, length + 1, dtype="float64")
    return s.rolling(length, min_periods=length).apply(
        lambda x: np.dot(x, weights) / weights.sum(), raw=True
    )


@INDICATORS.register("kama")
class KAMA(Indicator):
    """Kaufman Adaptive MA: an EMA whose smoothing scales with the efficiency ratio, so it
    tracks fast in trends and flattens in chop."""

    name = "kama"
    outputs = ("kama",)
    primary_param = "period"

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=10, ge=2)
        fast: int = Field(default=2, ge=1)
        slow: int = Field(default=30, ge=1)

        @model_validator(mode="after")
        def _check(self):
            if self.fast >= self.slow:
                raise ValueError("kama requires fast < slow")
            return self

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("close",))
        period, fast, slow = self.params["period"], self.params["fast"], self.params["slow"]
        close = df["close"]
        change = (close - close.shift(period)).abs()
        volatility = close.diff().abs().rolling(period, min_periods=period).sum()
        with np.errstate(divide="ignore", invalid="ignore"):
            er = change / volatility  # efficiency ratio; 0/0 (flat window) -> NaN
        fast_sc, slow_sc = 2.0 / (fast + 1), 2.0 / (slow + 1)
        sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2

        c = close.to_numpy(dtype="float64")
        s = sc.to_numpy(dtype="float64")
        n = len(c)
        kama = np.full(n, np.nan)
        if period < n:
            kama[period] = c[period]  # seed at the first bar with a defined ER
            for i in range(period + 1, n):
                kama[i] = kama[i - 1] + (0.0 if np.isnan(s[i]) else s[i]) * (c[i] - kama[i - 1])
        return build_output(df.index, {"kama": pd.Series(kama, index=df.index)})


@INDICATORS.register("hma")
class HMA(Indicator):
    """Hull Moving Average: WMA(2*WMA(n/2) - WMA(n), sqrt(n)) — fast and smooth."""

    name = "hma"
    outputs = ("hma",)
    primary_param = "period"

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=16, ge=2)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("close",))
        n = self.params["period"]
        raw = 2.0 * _wma(df["close"], n // 2) - _wma(df["close"], n)
        hma = _wma(raw, int(round(np.sqrt(n))))
        return build_output(df.index, {"hma": hma})


@INDICATORS.register("vortex")
class Vortex(Indicator):
    """Vortex Indicator: VI+ and VI- capture positive/negative trend movement."""

    name = "vortex"
    outputs = ("vi_plus", "vi_minus")
    primary_param = "period"

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=14, ge=1)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("high", "low", "close"))
        p = self.params["period"]
        vm_plus = (df["high"] - df["low"].shift(1)).abs()
        vm_minus = (df["low"] - df["high"].shift(1)).abs()
        tr_sum = true_range(df).rolling(p, min_periods=p).sum()
        return build_output(
            df.index,
            {
                "vi_plus": vm_plus.rolling(p, min_periods=p).sum() / tr_sum,
                "vi_minus": vm_minus.rolling(p, min_periods=p).sum() / tr_sum,
            },
        )
