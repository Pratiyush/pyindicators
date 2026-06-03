"""Momentum oscillators measuring the speed and extremity of price moves.

This module bundles the classic momentum family: RSI (Wilder, 1978), Rate of Change
and raw Momentum (standard price-difference indicators), the Stochastic oscillator
(Lane), the Commodity Channel Index (Lambert, 1980), and Williams %R (Larry Williams).
Several are bounded oscillators (RSI and Stochastic in [0, 100], Williams %R in
[-100, 0]); ROC, Momentum, and CCI oscillate around zero. All are trailing-only
(causal): every value is computed from current and prior bars, never future data.
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
    """Wilder's Relative Strength Index: momentum oscillator bounded [0, 100].

    What it is:
        A bounded momentum oscillator that gauges the magnitude of recent gains
        versus recent losses to flag overbought and oversold conditions. Created
        by J. Welles Wilder Jr. and introduced in 1978.

    How it works:
        Split each bar's price change into gains and losses, then smooth both with
        Wilder's running average (RMA) over the period. RS = avg gain / avg loss,
        and RSI = 100 - 100 / (1 + RS). Pure gains drive RSI toward 100, pure
        losses toward 0; a flat window with no gains or losses is left undefined.

    Best settings:
        Default period is 14 (Wilder's standard); typical range is 9-25. Use
        shorter periods (7-9) for faster, noisier signals in volatile markets and
        longer (21) for fewer false signals in slower markets.

    Interpretation:
        Above 70 is overbought, below 30 is oversold, and 50 is neutral.
        Price-versus-RSI divergences hint at trend weakness. Pitfall: in a strong
        trend RSI can stay overbought or oversold for long stretches, so it is not
        a standalone trade signal.

    Outputs:
        rsi -- the Relative Strength Index value in [0, 100].

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Wilder, New Concepts in Technical Trading Systems (1978).
    """

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
    """Rate of Change: percentage price change over the lookback period.

    What it is:
        A percentage-based momentum indicator that measures how fast price has
        moved relative to its level n bars ago. A standard technical-analysis
        oscillator centered on zero.

    How it works:
        ROC = (close / close n bars ago - 1) * 100. Positive values mean price is
        above its level n bars ago (upward momentum); negative values mean it is
        below (downward momentum). It rises and falls around the zero line.

    Best settings:
        Default period is 12; typical range is 5-20, with 9 and 14 also common for
        momentum work. Shorter periods increase sensitivity; longer periods track
        major momentum trends more smoothly.

    Interpretation:
        Above zero is bullish momentum, below zero is bearish; larger absolute
        values mean stronger momentum, and zero crossings flag direction changes.
        Pitfall: a high ROC while price falls can warn of a coming reversal rather
        than confirm strength.

    Outputs:
        roc -- percentage change over the period (zero-centered).

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: standard technical analysis; see StockCharts ChartSchool, Rate of Change.
    """

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
    """Raw price momentum: current close minus the close n bars ago.

    What it is:
        The simplest momentum measure: the absolute price difference between now
        and n bars ago, showing the velocity of price change. A standard
        technical-analysis indicator plotted around a zero line.

    How it works:
        Momentum = close - close n bars ago. Positive readings indicate upward
        momentum and negative readings downward; the magnitude reflects how much
        price has accelerated or decelerated over the window.

    Best settings:
        Default period is 10; typical range is 5-14. Shorter periods (5) are more
        responsive to recent swings, while longer periods (14) smooth the line.

    Interpretation:
        Zero-line crossovers signal momentum direction changes, and momentum
        peaks and troughs often lead price peaks and troughs. Pitfall: the output
        is in raw price units, so values are not comparable across instruments.

    Outputs:
        mom -- close minus close n bars ago, in price units (zero-centered).

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: standard technical analysis; see Tulip Indicators, Momentum (mom).
    """

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
    """Stochastic oscillator %K/%D (Lane): position in range, bounded [0, 100].

    What it is:
        A bounded momentum oscillator that locates the close within the recent
        high-low range, producing a smoothed %K line and its %D signal line.
        Popularized by George Lane.

    How it works:
        Raw %K = 100 * (close - lowest low) / (highest high - lowest low) over the
        lookback. %K is a smooth_k-period average of raw %K, and %D is a d-period
        average of %K. A close near the period high pushes the lines toward 100;
        near the period low, toward 0.

    Best settings:
        Defaults are k=14 (lookback), smooth_k=3 (%K smoothing), and d=3 (%D
        signal). Lookbacks of 5-14 are common; smoothing periods of 1-5 trade
        responsiveness for fewer whipsaws. Raise smoothing to calm choppy markets.

    Interpretation:
        Above 80 is overbought and below 20 is oversold; %K crossing above %D is a
        buy cue and crossing below is a sell cue. Pitfall: in strong trends the
        lines can pin near an extreme, so confirm with trend context.

    Outputs:
        stoch_k -- smoothed %K line in [0, 100].
        stoch_d -- %D signal line, a moving average of %K, in [0, 100].

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Lane's Stochastics; see StockCharts ChartSchool, Stochastic Oscillator.
    """

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
    """Commodity Channel Index: typical-price deviation oscillator (Lambert).

    What it is:
        An oscillator that measures how far the typical price sits from its moving
        average, scaled by mean deviation, to spot overbought/oversold extremes and
        cyclical turns. Developed by Donald Lambert in 1980.

    How it works:
        Typical price TP = (high + low + close) / 3. Take an SMA of TP over the
        period and the mean absolute deviation of TP from that SMA. CCI =
        (TP - SMA of TP) / (0.015 * mean deviation). The 0.015 constant keeps
        roughly 70-80 percent of readings within the +/-100 band.

    Best settings:
        Default period is 20 (standard); typical range is 10-40. Shorter periods
        (10-14) add sensitivity and volatility; longer periods (30-40) smooth
        readings and pull more values inside +/-100.

    Interpretation:
        Above +100 is an overbought/bullish extreme and below -100 is
        oversold/bearish; the +/-100 band holds most normal action, and zero
        crossings flag momentum shifts. Pitfall: it is unbounded, so extreme spikes
        can run well beyond +/-100 in strong moves.

    Outputs:
        cci -- the Commodity Channel Index value (zero-centered, unbounded).

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Lambert, Commodities magazine (1980); see StockCharts ChartSchool, CCI.
    """

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
    """Williams %R: close versus recent range on a negative scale, bounded [-100, 0].

    What it is:
        A bounded momentum oscillator that measures where the close sits within the
        recent high-low range, on an inverted scale from 0 down to -100. Developed
        by Larry Williams.

    How it works:
        Williams %R = -100 * (highest high - close) / (highest high - lowest low)
        over the lookback. A close at the period high gives 0 (strong uptrend); a
        close at the period low gives -100 (strong downtrend). It is effectively an
        inverted, unsmoothed cousin of Stochastic %K.

    Best settings:
        Default period is 14 (Larry Williams' standard); typical range is 5-20.
        Shorter periods increase sensitivity; longer periods reduce whipsaws.

    Interpretation:
        Above -20 is overbought and below -80 is oversold; rising toward 0 is
        bullish momentum and falling toward -100 is bearish. Pitfall: the inverted
        scale is the mirror of Stochastic, so do not confuse the bands.

    Outputs:
        willr -- Williams %R value in [-100, 0].

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Larry Williams; see StockCharts ChartSchool, Williams %R.
    """

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
