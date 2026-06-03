"""Adaptive and advanced trend indicators: KAMA, Hull MA, Vortex.

This module groups trend tools that go beyond fixed-window averaging. KAMA adapts its
smoothing to trend efficiency, HMA stacks weighted averages to cut lag while staying
smooth, and Vortex contrasts directional movement against true range to read trend
direction and strength. All are trailing-only (causal); warm-up rows are NaN.

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
    """Kaufman Adaptive Moving Average: an EMA whose smoothing adapts to trend efficiency.

    What it is:
        An adaptive moving average from Perry Kaufman that varies its sensitivity using the
        Efficiency Ratio (trend strength). It speeds up in clean trends and slows in choppy
        markets, filtering noise automatically. Part of the adaptive trend family.

    How it works:
        Efficiency Ratio ER = |close - close n bars ago| / sum of |close - prior close| over n.
        A smoothing constant SC = (ER * (fast_sc - slow_sc) + slow_sc) ^ 2, where fast_sc and
        slow_sc are the fast/slow EMA constants 2/(fast+1) and 2/(slow+1). Then
        KAMA = prev_KAMA + SC * (close - prev_KAMA), seeded at the first bar with a defined ER.

    Best settings:
        period default 10 (typical 5-50): shorter (5) reacts faster, longer (20-50) cuts noise.
        fast default 2 (typical 2-5): the fastest EMA constant; usually left at 2. slow default
        30 (typical 20-50): the slowest EMA constant; higher adds smoothing in choppy markets.
        Requires fast < slow.

    Interpretation:
        A flat KAMA means a low-trend, sideways market; a steep KAMA means a strong trend.
        Price breaking above KAMA is bullish, below is bearish. Pitfall: in very quiet ranges
        the efficiency ratio collapses, so KAMA barely moves and offers few signals.

    Outputs:
        kama -- the adaptive moving-average level.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Kaufman, Smarter Trading (1995); StockCharts ChartSchool, KAMA.
    """

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
    """Hull Moving Average: a fast, smooth trend line that combines weighted averages.

    What it is:
        A fast-responding moving average from Alan Hull (2005) that nests weighted moving
        averages to slash lag while keeping the line smooth. Part of the low-lag overlap
        family of trend indicators.

    How it works:
        Take wmaf = WMA(close, n/2) and wmas = WMA(close, n), then raw = 2*wmaf - wmas, which
        front-loads recent price. Finally HMA = WMA(raw, sqrt(n)). The three-step nesting
        removes lag more effectively than a single WMA or an EMA of the same length.

    Best settings:
        period default 16 (typical 9-50): about 9 for active, responsive trading and 20-30 for
        smoother swing trends. Internally it uses n/2 and round(sqrt(n)) sub-windows, so the
        effective warm-up is roughly n + sqrt(n) bars.

    Interpretation:
        Much faster than an EMA with minimal lag; use it for responsive trend following. Price
        crossing the HMA gives strong signals and a sharp slope change flags a momentum shift.
        Pitfall: its low lag can overshoot and whipsaw in choppy, non-trending markets.

    Outputs:
        hma -- the Hull moving-average level.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Hull, "How to reduce lag in a moving average" (2005); pandas-ta.
    """

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
    """Vortex Indicator: paired VI+ and VI- oscillators that read trend direction and strength.

    What it is:
        A trend indicator from Etienne Botes and Douglas Siepman (2010) built from two lines,
        VI+ and VI-, that measure positive and negative directional movement relative to true
        range. It identifies trend direction, strength, and reversals.

    How it works:
        Positive vortex movement VM+ = |high - prior low| and negative VM- = |low - prior high|.
        True range TR is the usual high/low/prior-close range. Then VI+ = sum(VM+, n) / sum(TR, n)
        and VI- = sum(VM-, n) / sum(TR, n). The trend is up when VI+ exceeds VI- and down when
        VI- exceeds VI+.

    Best settings:
        period default 14 (typical 7-30): 14 is standard; shorter (about 10) is more sensitive
        but risks whipsaws, longer (20-30) cuts false signals but may miss entries. Works best
        in trending markets and tends to chop in flat ranges.

    Interpretation:
        VI+ above VI- with widening separation signals an uptrend; VI- above VI+ signals a
        downtrend. Crossovers mark trend reversals and wider separation means a stronger trend.
        Pitfall: in sideways markets the two lines hover near each other and crossovers whipsaw.

    Outputs:
        vi_plus -- positive vortex movement ratio (VI+); dominance signals an uptrend.
        vi_minus -- negative vortex movement ratio (VI-); dominance signals a downtrend.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Botes and Siepman, "The Vortex Indicator," Technical Analysis of Stocks &
    Commodities (2010).
    """

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
