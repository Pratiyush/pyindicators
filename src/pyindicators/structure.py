"""Price-structure indicators: rolling extremes, Donchian channel, distance-from-extreme.

This module collects trailing-window support/resistance primitives that share one lineage:
the rolling highest-high and lowest-low over a lookback window (the same extremes that drive
Donchian channels, Stochastics, and Williams %R). It provides RollingHigh and RollingLow
(e.g. the ~52-week high/low at window=252), the three-line Donchian channel, and the
normalized PctFromHigh / PctFromLow distances used by breakout and trend-template screens
(such as Minervini's within-25%-of-high and 30%-above-low gates). Every indicator here is
trailing-only and causal, so no value depends on future bars.
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
    """Trailing maximum of the high over a lookback window (the rolling highest high).

    What it is:
        The highest ``high`` observed over the last ``window`` bars, recomputed each bar as
        the window slides forward. With daily data and window=252 it is the classic ~52-week
        high. It is the upper-extreme primitive shared by Donchian, Stochastics and Aroon.

    How it works:
        For each bar, take the maximum of the high column over the trailing window of length
        ``window`` (inclusive of the current bar). The result is a step-wise ceiling that only
        rises when a new high prints and otherwise holds flat until older highs drop out.

    Best settings:
        Default window=252 (about one trading year, the 52-week high). Common alternatives
        are 20-55 for breakout/Donchian-style channels and 20/63/126 for monthly, quarterly,
        and half-year highs. Shorter windows react faster; longer windows mark major levels.

    Interpretation:
        Price touching or exceeding the rolling high signals a breakout / new-high momentum;
        sustained distance below it shows weakness. Pitfall: a flat line just means no new
        high in the window, not necessarily a downtrend.

    Outputs:
        rolling_high -- the maximum high over the trailing window.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Donchian, highest-high-over-N convention; 52-week-high screening practice.
    """

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
    """Trailing minimum of the low over a lookback window (the rolling lowest low).

    What it is:
        The lowest ``low`` observed over the last ``window`` bars, recomputed each bar as the
        window slides forward. With daily data and window=252 it is the classic ~52-week low.
        It is the lower-extreme primitive shared by Donchian, Stochastics and Aroon.

    How it works:
        For each bar, take the minimum of the low column over the trailing window of length
        ``window`` (inclusive of the current bar). The result is a step-wise floor that only
        falls when a new low prints and otherwise holds flat until older lows drop out.

    Best settings:
        Default window=252 (about one trading year, the 52-week low). Common alternatives are
        20-55 for breakdown/Donchian-style channels and 20/63/126 for monthly, quarterly, and
        half-year lows. Shorter windows react faster; longer windows mark major support.

    Interpretation:
        Price touching or undercutting the rolling low signals a breakdown / new-low weakness;
        sustained distance above it shows resilience. Pitfall: a flat line just means no new
        low in the window, not necessarily an uptrend.

    Outputs:
        rolling_low -- the minimum low over the trailing window.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Donchian, lowest-low-over-N convention; 52-week-low screening practice.
    """

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
    """Donchian channel: trailing highest-high, lowest-low, and their midline.

    What it is:
        A volatility/support-resistance envelope that bands price between the highest high and
        lowest low of a lookback window, with a middle line at their average. Popularized by
        trend-follower Richard Donchian and central to classic breakout systems.

    How it works:
        Upper band = highest high over the last ``window`` bars; lower band = lowest low over
        the same window; middle band = (upper + lower) / 2. All three recompute each bar as the
        window slides, so band width directly reflects the recent trading range (volatility).

    Best settings:
        Default window=20 (the standard intraday/short-term setting). Typical range is 10-50:
        shorter (10-14) tracks recent extremes and triggers breakouts sooner, while longer
        (50+) marks broader, longer-term support/resistance. 20 and 55 are common Turtle values.

    Interpretation:
        A close above the upper band signals a bullish breakout; below the lower band, a
        bearish breakdown. The midline acts as midpoint support/resistance and a trend gauge.
        Pitfall: narrow bands flag consolidation, not a directional signal on their own.

    Outputs:
        dc_upper -- highest high over the window (upper band).
        dc_lower -- lowest low over the window (lower band).
        dc_mid -- midline, (dc_upper + dc_lower) / 2.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Richard Donchian; en.wikipedia.org/wiki/Donchian_channel.
    """

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
    """Fractional distance of close below the trailing high; always <= 0 (0 = at the high).

    What it is:
        How far the current close sits below the rolling highest high, expressed as a signed
        fraction. It is the rolling-drawdown-from-peak distance behind 52-week-high momentum
        ranks and within-X%-of-high gates (e.g. Minervini's within-25%-of-high screen).

    How it works:
        Compute the highest high over the last ``window`` bars, then return
        close / rolling_high - 1. The value is 0 when price makes a new high and increasingly
        negative as price pulls back; -0.25 means the close is 25 percent below the window high.

    Best settings:
        Default window=252 (about one year, the 52-week high). Use 20-63 for swing/breakout
        proximity and 252 for position/leadership screens. Threshold rules vary: within 25
        percent of the high (>= -0.25) is a common Minervini-style trend-template gate.

    Interpretation:
        Values near 0 mean price is hugging its high (strength/breakout proximity); deeply
        negative values mean a large drawdown from the peak. Pitfall: the floor is open-ended,
        so it cannot be read as a bounded oscillator.

    Outputs:
        pct_from_high -- close / rolling_high - 1 (<= 0; 0 at a new high).

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: 52-week-high distance convention; Minervini trend-template proximity gates.
    """

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
    """Fractional distance of close above the trailing low; always >= 0 (0 = at the low).

    What it is:
        How far the current close sits above the rolling lowest low, expressed as a signed
        fraction. It is the rise-off-the-bottom distance behind 52-week-low recovery screens
        and above-X%-of-low gates (e.g. Minervini's 30-percent-above-low requirement).

    How it works:
        Compute the lowest low over the last ``window`` bars, then return
        close / rolling_low - 1. The value is 0 when price makes a new low and grows as price
        recovers; 0.30 means the close is 30 percent above the window low.

    Best settings:
        Default window=252 (about one year, the 52-week low). Use 20-63 for swing/recovery
        proximity and 252 for position/leadership screens. Threshold rules vary: at least 30
        percent above the low (>= 0.30) is a common Minervini-style trend-template gate.

    Interpretation:
        Larger values mean price has lifted well off its low (recovery/strength); values near
        0 mean price is sitting on its low (weakness). Pitfall: it is unbounded above, so it
        cannot be read as a bounded oscillator.

    Outputs:
        pct_from_low -- close / rolling_low - 1 (>= 0; 0 at a new low).

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: 52-week-low distance convention; Minervini trend-template proximity gates.
    """

    name = "pct_from_low"
    outputs = ("pct_from_low",)
    primary_param = "window"
    params_model = _Window

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("low", "close"))
        w = self.params["window"]
        ll = df["low"].rolling(w, min_periods=w).min()
        return build_output(df.index, {"pct_from_low": df["close"] / ll - 1.0})
