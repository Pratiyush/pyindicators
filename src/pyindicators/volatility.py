"""Volatility indicators measuring the size of price movement, not its direction.

This module collects the classic dispersion and range-based tools: ATR (Average True Range),
Bollinger Bands, Keltner Channels, rolling standard deviation, and the TTM Squeeze that fuses
Bollinger Bands with Keltner Channels. They share a common lineage in technical analysis:
Wilder's True Range underpins ATR, Keltner Channels, and the Squeeze, while Bollinger Bands and
StdDev quantify dispersion around a moving average. All are trailing-only (causal) and read only
completed bars, so warm-up rows are NaN until the lookback window fills.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from .base import Indicator
from .common import build_output, ema, require_columns, true_range, wilder_rma
from .registry import INDICATORS


@INDICATORS.register("atr")
class ATR(Indicator):
    """Average True Range: a smoothed measure of price volatility (always non-negative).

    What it is:
        A volatility gauge from J. Welles Wilder Jr. (1978) that averages the True Range to
        quantify how much price typically moves per bar. It captures gaps and limit moves, not
        just the high-low range, and is direction-agnostic. Part of the volatility family.

    How it works:
        Two stages. True Range per bar = max(high - low, abs(high - prior close),
        abs(low - prior close)). ATR then smooths TR with Wilder's RMA: the first value seeds
        on a simple average and each later value is (prior ATR * (n - 1) + current TR) / n.

    Best settings:
        period default 14 (Wilder's original, the most common). Typical range 10-22: shorter
        (10-12) reacts faster to volatility shifts, longer (18-22) smooths more. Match the period
        to your timeframe. To compare ATR across instruments, normalize it (e.g. NATR).

    Interpretation:
        Rising ATR means expanding volatility; falling ATR means contracting volatility. ATR
        approximates a typical bar's range and is widely used to size stops and positions. It
        gives no directional signal; do not read high ATR as bullish or bearish on its own.

    Outputs:
        atr -- Wilder-smoothed average of True Range over the period.
        tr -- the raw, unsmoothed True Range for each bar.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Wilder, New Concepts in Technical Trading Systems (1978).
    """

    name = "atr"
    outputs = ("atr", "tr")
    primary_param = "period"

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=14, ge=1)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("high", "low", "close"))
        tr = true_range(df)
        atr = wilder_rma(tr, self.params["period"])
        return build_output(df.index, {"atr": atr, "tr": tr})


@INDICATORS.register("bbands")
class BollingerBands(Indicator):
    """Bollinger Bands: a moving-average envelope whose width tracks volatility.

    What it is:
        A volatility overlay from John Bollinger (1980s) made of three bands around price. The
        middle band is a simple moving average; the upper and lower bands sit a number of
        standard deviations away, so the envelope expands and contracts with volatility.

    How it works:
        Mid = SMA(close, period). Upper = mid + num_std * stdev, lower = mid - num_std * stdev,
        where stdev is the population standard deviation of close over the window. Width is
        reported as (upper - lower) / mid, and %B as (close - lower) / (upper - lower).

    Best settings:
        period default 20 (standard for daily charts); typical 10-50, with 5-10 for fast/scalping
        and 50+ for long-term trends. num_std default 2.0 (roughly 95% of action inside the band);
        typical 1.5-3, using ~1.5 for tighter sensitivity and 2.5-3 for wider bands.

    Interpretation:
        Price near the upper band is relatively high (possible pullback), near the lower band
        relatively low (possible bounce). Narrow bands (a squeeze) flag low volatility that often
        precedes a breakout; a band walk signals a strong trend. Touches alone are not signals.

    Outputs:
        bb_mid -- the SMA middle band (period-length simple moving average of close).
        bb_upper -- middle band plus num_std population standard deviations.
        bb_lower -- middle band minus num_std population standard deviations.
        bb_width -- band span normalized by the middle band: (upper - lower) / mid.
        bb_pctb -- position of close within the bands: (close - lower) / (upper - lower).

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Bollinger, Bollinger on Bollinger Bands (2001).
    """

    name = "bbands"
    outputs = ("bb_mid", "bb_upper", "bb_lower", "bb_width", "bb_pctb")
    primary_param = "period"

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=20, ge=2)
        num_std: float = Field(default=2.0, gt=0)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("close",))
        p, k = self.params["period"], self.params["num_std"]
        mid = df["close"].rolling(p, min_periods=p).mean()
        sd = df["close"].rolling(p, min_periods=p).std(ddof=0)
        upper = mid + k * sd
        lower = mid - k * sd
        width = (upper - lower) / mid
        pctb = (df["close"] - lower) / (upper - lower)
        return build_output(
            df.index,
            {
                "bb_mid": mid,
                "bb_upper": upper,
                "bb_lower": lower,
                "bb_width": width,
                "bb_pctb": pctb,
            },
        )


@INDICATORS.register("keltner")
class KeltnerChannels(Indicator):
    """Keltner Channels: an EMA-centered volatility envelope sized by ATR.

    What it is:
        A volatility envelope attributed to Chester Keltner and later reworked with ATR by Linda
        Bradford Raschke. Like Bollinger Bands but using an EMA midline and Average True Range
        (instead of standard deviation) for band width, making it smoother in gappy markets.

    How it works:
        Mid = EMA(close, period). Upper = mid + mult * ATR, lower = mid - mult * ATR, where ATR
        is Wilder's smoothed True Range over atr_period. Because ATR includes gaps, the channel
        reacts to true range spikes rather than to dispersion of the closes alone.

    Best settings:
        period default 20 (EMA midline); typical 10-30, shorter for responsiveness, longer for
        smoothing. atr_period default 10; typical 8-14. mult default 2.0 (band distance);
        typical 1.5-3, tighter values for ranging markets and wider for volatile ones.

    Interpretation:
        Price above the upper band suggests an overbought or strongly trending state; below the
        lower band, oversold or weak. Narrowing bands signal a squeeze with a breakout pending.
        Keltner tends to give fewer false signals than Bollinger Bands when markets gap.

    Outputs:
        kc_mid -- the EMA middle band (period-length exponential moving average of close).
        kc_upper -- middle band plus mult * ATR(atr_period).
        kc_lower -- middle band minus mult * ATR(atr_period).

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Keltner, How to Make Money in Commodities (1960); ATR variant per Raschke.
    """

    name = "keltner"
    outputs = ("kc_mid", "kc_upper", "kc_lower")
    primary_param = "period"

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=20, ge=1)
        atr_period: int = Field(default=10, ge=1)
        mult: float = Field(default=2.0, gt=0)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("high", "low", "close"))
        mid = ema(df["close"], self.params["period"])
        atr = wilder_rma(true_range(df), self.params["atr_period"])
        mult = self.params["mult"]
        return build_output(
            df.index,
            {"kc_mid": mid, "kc_upper": mid + mult * atr, "kc_lower": mid - mult * atr},
        )


@INDICATORS.register("stdev")
class StdDev(Indicator):
    """Rolling population standard deviation of close: a raw volatility measure (non-negative).

    What it is:
        The population standard deviation of closing prices over a lookback window, a basic
        statistic that quantifies how widely price disperses around its own mean. It is the same
        dispersion measure that drives Bollinger Bands and many other volatility tools.

    How it works:
        Over the trailing window, stdev = sqrt(sum((close - mean)^2) / n), dividing by n (the
        population form, ddof = 0) rather than n - 1. Larger deviations of close from the window
        mean produce a larger value; the result is in the same price units as close.

    Best settings:
        period default 20 here for a smoother volatility read; typical 5-20, with shorter windows
        (around 5) giving a faster, noisier signal and longer windows smoothing it. Pair with a
        moving average to build bands (mean +/- k * stdev), where k is the band multiplier.

    Interpretation:
        A single non-negative value: higher means greater volatility, lower means calmer price.
        Rising stdev marks expanding volatility, falling stdev marks contraction. It is not
        directional and says nothing about whether price is going up or down.

    Outputs:
        stdev -- population standard deviation (ddof = 0) of close over the period.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: standard statistic; cf. TA-Lib STDDEV; Bollinger on Bollinger Bands (2001).
    """

    name = "stdev"
    outputs = ("stdev",)
    primary_param = "period"

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=20, ge=2)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("close",))
        p = self.params["period"]
        return build_output(
            df.index, {"stdev": df["close"].rolling(p, min_periods=p).std(ddof=0)}
        )


@INDICATORS.register("ttm_squeeze")
class TTMSqueeze(Indicator):
    """TTM Squeeze (Carter): a volatility-compression flag from Bollinger Bands inside Keltner.

    What it is:
        John Carter's TTM Squeeze, a low-volatility detector that compares Bollinger Bands to
        Keltner Channels. When the bands contract inside the channel, volatility is compressed and
        a breakout often follows once it releases. Part of the volatility/momentum family.

    How it works:
        Build Bollinger Bands (SMA mid, num_std population stdev) and a Keltner-style channel
        (EMA mid, kc_mult * ATR over atr_period), all on the same period. The squeeze is ON
        (1.0) while the Bollinger band sits fully inside the Keltner channel, else OFF (0.0).

    Best settings:
        period default 20 (shared by both bands); typical 15-25. num_std default 2.0 (typical
        1.5-2.5; lower for tighter detection). kc_mult default 1.5 (the classic "normal" Keltner
        scalar). atr_period default 20. Combine with a trend filter; the squeeze is not a side.

    Interpretation:
        ttm_squeeze = 1.0 marks a quiet, coiled market; the transition from 1.0 to 0.0 ("the
        squeeze fires") flags expansion and a potential breakout. ttm_momentum gives the likely
        direction. A long squeeze without firing can persist; do not pre-empt the release.

    Outputs:
        ttm_squeeze -- 1.0 while Bollinger Bands are inside the Keltner channel, else 0.0.
        ttm_momentum -- close minus the SMA midline, a simple momentum/direction proxy.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Carter, Mastering the Trade (2005).
    """

    name = "ttm_squeeze"
    outputs = ("ttm_squeeze", "ttm_momentum")
    # primary_param left None so columns stay ttm_squeeze/ttm_momentum (single instance use).
    bounds = {"ttm_squeeze": (0.0, 1.0)}

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=20, ge=2)
        num_std: float = Field(default=2.0, gt=0)
        kc_mult: float = Field(default=1.5, gt=0)
        atr_period: int = Field(default=20, ge=1)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("high", "low", "close"))
        p = self.params["period"]
        close = df["close"]
        mid = close.rolling(p, min_periods=p).mean()
        sd = close.rolling(p, min_periods=p).std(ddof=0)
        bb_upper = mid + self.params["num_std"] * sd
        bb_lower = mid - self.params["num_std"] * sd
        kc_mid = ema(close, p)
        atr = wilder_rma(true_range(df), self.params["atr_period"])
        kc_upper = kc_mid + self.params["kc_mult"] * atr
        kc_lower = kc_mid - self.params["kc_mult"] * atr
        squeeze = ((bb_upper <= kc_upper) & (bb_lower >= kc_lower)).astype("float64")
        squeeze = squeeze.where(bb_upper.notna() & kc_upper.notna())  # NaN during warm-up
        return build_output(df.index, {"ttm_squeeze": squeeze, "ttm_momentum": close - mid})
