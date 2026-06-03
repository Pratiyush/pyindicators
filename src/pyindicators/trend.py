"""Trend indicators: moving averages, slope, MACD, ADX, Aroon.

This module collects the workhorse trend-following tools. The moving averages (SMA,
EMA, WMA) and SMASlope smooth price to expose direction; MACD measures the spread
between two EMAs; ADX/DMI gauges trend strength via directional movement; and Aroon
times how recently new extremes occurred. They share a common lineage in classic
charting: moving averages (Murphy, Technical Analysis of the Financial Markets),
MACD (Appel 1979), ADX/DMI (Wilder 1978), and Aroon (Chande 1995). All are
trailing-only (causal) and vectorized over pandas Series.
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
    """Unweighted mean of the last N closing prices; the most basic moving average.

    What it is:
        The simple moving average (SMA), an arithmetic mean of price over a rolling
        window. It is the foundational smoothing filter in technical analysis and
        treats every bar in the window equally.

    How it works:
        Sum the last N closing prices and divide by N. Each new bar drops the oldest
        price and adds the newest, so the average glides forward one step at a time.
        Longer windows smooth more but lag more.

    Best settings:
        Default period is 50. Typical range is 5-200: 5-20 for short-term, 20-50 for
        swing trading, and 50-200 for long-term trend (the 50 and 200 SMAs drive the
        golden/death cross). Shorten for responsiveness, lengthen for smoother signals.

    Interpretation:
        Price above the SMA suggests an uptrend, below it a downtrend, and the slope
        hints at trend strength. The SMA often acts as dynamic support/resistance. The
        pitfall: it lags, so crossovers can arrive late and whipsaw in ranging markets.

    Outputs:
        sma -- the rolling arithmetic mean of close over the period.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Murphy, Technical Analysis of the Financial Markets (1999).
    """

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
    """Recursive moving average that weights recent prices more, cutting lag vs SMA.

    What it is:
        The exponential moving average (EMA), a weighted moving average where weights
        decay exponentially into the past. A staple smoothing filter, it reacts faster
        to new prices than the equal-weighted SMA while still damping noise.

    How it works:
        EMA(today) = alpha * close + (1 - alpha) * EMA(yesterday), with the smoothing
        factor alpha = 2 / (period + 1). A higher alpha (shorter period) makes the line
        more responsive; older data fades but never fully leaves the calculation. This
        implementation uses adjust=False, a pure recursive update seeded from the start.

    Best settings:
        Default period is 20. Typical range is 5-200: 9-12 for short-term, 21-50 for
        medium, 50-200 for long-term, and the 12/26 pair feeds MACD. Shorten for quicker
        turns, lengthen for steadier trend confirmation.

    Interpretation:
        Price above the EMA suggests an uptrend, below it a downtrend, and a steeper
        slope means a stronger trend. EMA crossovers flag momentum shifts. The pitfall:
        being responsive, it can generate more false signals than the SMA in chop.

    Outputs:
        ema -- the exponentially weighted moving average of close.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Murphy, Technical Analysis of the Financial Markets (1999).
    """

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
    """Moving average with linearly declining weights, most recent price heaviest.

    What it is:
        The weighted moving average (WMA), a moving average that assigns linearly
        increasing weights to more recent prices. It sits between the SMA and EMA in
        responsiveness: more reactive than the SMA, less so than the EMA.

    How it works:
        WMA = (P1*1 + P2*2 + ... + Pn*n) / (1 + 2 + ... + n), where the newest bar gets
        weight n and the oldest gets weight 1. The denominator is the triangular number
        n*(n+1)/2. The linear taper emphasizes recent action while still using the full
        window.

    Best settings:
        Default period is 20. Typical range is 5-100: about 10-20 for swing trading, 5
        for a faster response, and 50+ for longer trends. Shorten to track price more
        tightly, lengthen to smooth.

    Interpretation:
        Price above the WMA suggests an uptrend, below it a downtrend; slope and
        crossovers signal trend changes. The pitfall: like all moving averages it lags
        and can whipsaw in sideways markets, though less than an equal-weighted SMA.

    Outputs:
        wma -- the linearly weighted moving average of close.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Murphy, Technical Analysis of the Financial Markets (1999).
    """

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
    """Per-bar rate of change of an SMA, measuring whether the trend line is rising.

    What it is:
        The slope of a simple moving average: the average price change per bar of the
        SMA over a lookback span. It turns a smoothing filter into a directional gauge,
        widely used in stage-analysis style screening.

    How it works:
        slope = (SMA - SMA shifted back by lookback) / lookback. It is the discrete
        first difference of the SMA divided by the number of bars between the two
        samples, giving a per-bar rise expressed in price units.

    Best settings:
        Defaults are period 200 (the SMA window) and lookback 22 (about one trading
        month). The 200/22 pairing supports Minervini/Weinstein "the 200-day MA is
        rising" checks. Use a longer SMA for the primary trend; widen lookback to smooth
        the slope, shorten it to react sooner.

    Interpretation:
        Slope above zero means the SMA is rising (trend up), below zero means falling
        (trend down), and the magnitude reflects how fast. The pitfall: a longer SMA
        and lookback add lag, so the slope can stay positive into the start of a top.

    Outputs:
        sma_slope -- per-bar change of the SMA over the lookback span, in price units.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Murphy, Technical Analysis of the Financial Markets (1999); Weinstein,
    Secrets for Profiting in Bull and Bear Markets (1988).
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
    """Trend-following momentum indicator built from the spread of two EMAs.

    What it is:
        Moving Average Convergence/Divergence (MACD), created by Gerald Appel in the
        late 1970s. It measures the relationship between a fast and a slow exponential
        moving average and is one of the most widely used momentum tools.

    How it works:
        MACD line = fast EMA minus slow EMA (default 12 minus 26). The signal line is a
        9-period EMA of the MACD line, and the histogram is MACD minus signal. A positive
        MACD means the fast EMA leads the slow EMA (bullish bias). All EMAs run from the
        first bar with no warm-up trimming, per convention.

    Best settings:
        Defaults are fast 12, slow 26, signal 9 (the standard set). Fast typically
        5-20, slow 20-50, signal 5-15. Params must satisfy fast < slow. Shorter fast or
        signal periods add sensitivity and more crossovers; longer ones cut false signals.

    Interpretation:
        MACD above its signal is bullish, below is bearish, and a cross is a buy or sell
        cue. Divergence between price and MACD warns of reversals; histogram size shows
        momentum. The pitfall: the first ~25-35 bars are unreliable while the EMAs settle.

    Outputs:
        macd -- fast EMA minus slow EMA (the MACD line).
        macd_signal -- EMA of the MACD line over the signal period.
        macd_hist -- MACD line minus signal line (the histogram).

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Appel, technical analysis writings (1979).
    """

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
    """Trend-strength gauge (0-100) with +DI/-DI direction, from Wilder's DMI.

    What it is:
        The Average Directional Index (ADX) plus the directional indicators that make
        up Wilder's Directional Movement System. ADX rates how strong a trend is,
        regardless of direction; +DI and -DI show which side is in control.

    How it works:
        From bar-to-bar highs and lows, derive plus and minus directional movement
        (+DM, -DM) and the true range. Wilder-smooth each over the period, then
        +DI = 100 * smoothed +DM / smoothed TR and likewise for -DI. DX = 100 *
        |+DI - -DI| / (+DI + -DI), and ADX is the Wilder-smoothed DX. All outputs
        sit on a 0-100 scale.

    Best settings:
        Default period is 14 (Wilder's standard); typical range 10-28. Shorter periods
        react faster to trend shifts, longer periods smooth noise. Note that Wilder
        smoothing needs roughly 150 bars to fully converge to stable values.

    Interpretation:
        ADX above 25 signals a strong trend, 20-25 is a gray zone, below 20 means weak
        or no trend; rising ADX strengthens, falling weakens. +DI over -DI is bullish,
        the reverse bearish. The pitfall: ADX gives no direction and lags reversals.

    Outputs:
        adx -- Wilder-smoothed directional index; trend strength on a 0-100 scale.
        plus_di -- positive directional indicator (0-100); upward pressure.
        minus_di -- negative directional indicator (0-100); downward pressure.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Wilder, New Concepts in Technical Trading Systems (1978).
    """

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
    """Pair of 0-100 oscillators timing how recently the period high/low occurred.

    What it is:
        The Aroon indicator, developed by Tushar Chande in 1995. Its name means "dawn":
        it aims to spot the early light of a new trend by measuring time since extremes
        rather than price levels. Aroon Up and Aroon Down each range 0-100.

    How it works:
        Aroon Up = ((period - bars since the highest high) / period) * 100, and Aroon
        Down uses the lowest low the same way. A fresh high today drives Aroon Up to
        100; the longer ago the extreme, the lower the value. The window here includes
        the current bar.

    Best settings:
        Default period is 25 (Chande's standard); typical range 14-28. A shorter period
        (e.g. 14) is more sensitive and signals sooner; a longer one is smoother and
        flags only major trends.

    Interpretation:
        Aroon Up sustained above 70 marks a strong uptrend, Aroon Down above 70 a strong
        downtrend; the lines crossing flags a trend change. Both near 50 means
        consolidation. The pitfall: in a flat range the lines whipsaw and mislead.

    Outputs:
        aroon_up -- 0-100 score; how recently the period's highest high occurred.
        aroon_down -- 0-100 score; how recently the period's lowest low occurred.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Chande, Aroon indicator, Technical Analysis of Stocks & Commodities (1995).
    """

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
