"""Volume indicators: OBV, VWAP, relative volume, volume SMA, MFI, Force Index.

This module collects classic price-volume tools that gauge accumulation, distribution,
and participation. They share a common lineage in volume-confirmation analysis: OBV
(Granville 1963) accumulates signed volume, VWAP weights typical price by volume, MFI
(Quong and Soudack) is a volume-weighted RSI, Elder's Force Index marries price change
with volume, and relative volume and volume SMA normalize raw turnover. All are
trailing-only (causal), computing each bar solely from completed historical data.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from .base import Indicator
from .common import build_output, ema, require_columns, typical_price
from .registry import INDICATORS


@INDICATORS.register("obv")
class OBV(Indicator):
    """On-Balance Volume: a cumulative running total of signed volume (starts at 0).

    What it is:
        A volume-based momentum indicator created by Joseph Granville (1963). It treats
        each day's volume as a vote of buying or selling pressure, building a single
        accumulation/distribution line from price direction and turnover.

    How it works:
        Maintains a running total: if close is above the prior close, add the current
        volume; if below, subtract it; if unchanged, leave the total as is. The series
        begins at an initial value (here 0) and accumulates signed volume thereafter.

    Best settings:
        No parameters. Reads directly off any timeframe. The absolute level is arbitrary
        and depends on the start point, so always interpret OBV by its slope and the
        position of its swing highs/lows, not its raw value.

    Interpretation:
        Rising OBV signals accumulation (bullish); falling OBV signals distribution
        (bearish). Divergence between OBV and price can foreshadow reversals, and OBV
        confirming a price breakout adds conviction. Pitfall: the level itself is
        meaningless; only direction and divergences matter.

    Outputs:
        obv -- cumulative signed-volume total; positive volume on up bars, negative on
            down bars, zero on unchanged bars.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Granville, New Key to Stock Market Profits (1963); StockCharts ChartSchool.
    """

    name = "obv"
    outputs = ("obv",)

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("close", "volume"))
        direction = np.sign(df["close"].diff().fillna(0.0))
        obv = (direction * df["volume"]).cumsum()
        return build_output(df.index, {"obv": obv})


@INDICATORS.register("vwap")
class VWAP(Indicator):
    """Volume-weighted average price: typical price averaged by traded volume.

    What it is:
        The average price of an asset weighted by trading volume, originally an
        institutional benchmark for judging execution quality and now a widely used
        intraday dynamic support/resistance level. Common in the FinTA lineage.

    How it works:
        VWAP = cumulative(typical price * volume) / cumulative(volume), where typical
        price = (high + low + close) / 3. Each bar's contribution is scaled by its
        volume, so heavily traded prices pull the line toward them.

    Best settings:
        Parameter ``anchor`` (default "cumulative"). Cumulative anchors from the start
        of the frame; the "session" anchor (daily/weekly reset for intraday use) needs a
        trading calendar and is not yet implemented, so it falls back to cumulative. Use
        intraday data for the classic institutional reading.

    Interpretation:
        Price above VWAP signals buying strength; price below signals selling pressure.
        VWAP often acts as support on pullbacks or resistance on bounces, and mean-
        reversion setups fade large gaps from it. Pitfall: without a session reset it is
        not meaningful for multi-day trend analysis.

    Outputs:
        vwap -- volume-weighted average of typical price from the anchor point forward.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: standard execution benchmark; FinTA; StockCharts ChartSchool (VWAP).
    """

    name = "vwap"
    outputs = ("vwap",)

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        anchor: str = Field(default="cumulative", pattern="^(cumulative|session)$")

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("high", "low", "close", "volume"))
        tp = typical_price(df)
        cum_pv = (tp * df["volume"]).cumsum()
        cum_v = df["volume"].cumsum()
        return build_output(df.index, {"vwap": cum_pv / cum_v})


@INDICATORS.register("rvol")
class RelativeVolume(Indicator):
    """Relative volume (RVOL): current volume divided by its trailing average.

    What it is:
        A participation gauge popularized in the IBD/O'Neil school of analysis. It
        expresses today's volume as a multiple of the recent norm, so 1.0 is an average
        day and 2.0 is twice the usual turnover, regardless of the stock's typical scale.

    How it works:
        Divides the current bar's volume by a simple moving average of volume over a
        trailing window. The window is excluded from being counted twice only in the
        sense that it is a plain rolling mean ending at the current bar.

    Best settings:
        Parameter ``window`` (default 50). Longer windows give a steadier baseline for
        spotting unusual activity; shorter windows react faster but are noisier. Adjust
        to the holding horizon and the data's timeframe.

    Interpretation:
        Values well above 1.0 mark unusually heavy trading, which lends conviction to
        breakouts or breakdowns; values below 1.0 mark quiet sessions. Pitfall: RVOL says
        nothing about direction, so pair it with a price signal.

    Outputs:
        rvol -- ratio of current volume to its trailing-average volume (1.0 = average).

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: relative-volume convention; IBD/O'Neil usage (How to Make Money in Stocks).
    """

    name = "rvol"
    outputs = ("rvol",)
    primary_param = "window"

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        window: int = Field(default=50, ge=1)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("volume",))
        w = self.params["window"]
        avg = df["volume"].rolling(w, min_periods=w).mean()
        return build_output(df.index, {"rvol": df["volume"] / avg})


@INDICATORS.register("vol_sma")
class VolumeSMA(Indicator):
    """Simple moving average of volume: the rolling-mean turnover baseline.

    What it is:
        A plain arithmetic average of trading volume over a fixed lookback. It is the
        standard reference line drawn beneath a volume histogram to define what a
        "normal" day of turnover looks like for a given instrument.

    How it works:
        Averages the volume of the last N bars with equal weight, sliding the window
        forward one bar at a time. Each point is simply the sum of the window's volume
        divided by the number of bars.

    Best settings:
        Parameter ``period`` (default 50). Longer periods smooth more and define a slower
        baseline; shorter periods track recent activity more closely. Choose to match the
        timeframe and how reactive a baseline you want.

    Interpretation:
        Bars above the average flag heavier-than-usual participation; bars below it flag
        lighter trading. It underpins ratio measures such as relative volume. Pitfall:
        like any equal-weight mean, it lags abrupt shifts in activity.

    Outputs:
        vol_sma -- equal-weighted average of volume over the trailing period.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: standard simple-moving-average construction applied to the volume series.
    """

    name = "vol_sma"
    outputs = ("vol_sma",)
    primary_param = "period"

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=50, ge=1)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("volume",))
        p = self.params["period"]
        return build_output(
            df.index, {"vol_sma": df["volume"].rolling(p, min_periods=p).mean()}
        )


@INDICATORS.register("mfi")
class MoneyFlowIndex(Indicator):
    """Money Flow Index: a volume-weighted RSI on typical price, bounded [0, 100].

    What it is:
        A momentum oscillator (Quong and Soudack) that folds volume into an RSI-style
        calculation to measure buying and selling pressure. By weighting moves with
        volume it can flag overbought/oversold turns more reliably than price-only RSI.

    How it works:
        Typical price = (high + low + close) / 3, and raw money flow = typical price *
        volume. Each bar's flow is tagged positive or negative by whether typical price
        rose or fell. Over n bars, money ratio = sum(positive flow) / sum(negative flow),
        and MFI = 100 - 100 / (1 + ratio), giving a 0-100 reading.

    Best settings:
        Parameter ``period`` (default 14, typical 10-20). Fourteen is standard; shorter
        periods raise sensitivity to volume shifts, longer periods smooth noise. A flat
        window with neither up- nor down-flow is undefined and returns NaN.

    Interpretation:
        Above 80 is overbought and below 20 is oversold, with 50 as equilibrium.
        Price/MFI divergence warns of a weakening trend. Pitfall: in strong trends MFI
        can stay pinned at an extreme, so do not fade extremes mechanically.

    Outputs:
        mfi -- volume-weighted money-flow oscillator on a 0-100 scale.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Quong and Soudack; StockCharts ChartSchool (Money Flow Index).
    """

    name = "mfi"
    outputs = ("mfi",)
    primary_param = "period"
    bounds = {"mfi": (0.0, 100.0)}

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=14, ge=1)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("high", "low", "close", "volume"))
        p = self.params["period"]
        tp = typical_price(df)
        raw_flow = tp * df["volume"]
        up = tp > tp.shift(1)
        down = tp < tp.shift(1)
        pos = raw_flow.where(up, 0.0).rolling(p, min_periods=p).sum()
        neg = raw_flow.where(down, 0.0).rolling(p, min_periods=p).sum()
        with np.errstate(divide="ignore", invalid="ignore"):
            mfr = pos / neg                    # pure inflow => inf => mfi 100
            mfi = 100.0 - 100.0 / (1.0 + mfr)  # pure outflow => mfr 0 => mfi 0
        # A flat window (no up- and no down-money-flow) is undefined -> NaN.
        mfi = mfi.mask((pos == 0) & (neg == 0))
        return build_output(df.index, {"mfi": mfi})


@INDICATORS.register("force_index")
class ForceIndex(Indicator):
    """Elder's Force Index: an EMA-smoothed product of price change and volume.

    What it is:
        A volume-based momentum indicator from Alexander Elder that combines the size of
        a price move with the volume behind it to gauge the force of buyers versus
        sellers. Smoothing turns the raw, spiky measure into a usable oscillator.

    How it works:
        Raw force = close.diff() * volume for each bar, then an exponential moving average
        of that raw series. A positive value means price rose on its volume (buying
        force); a negative value means price fell on its volume (selling force).

    Best settings:
        Parameter ``period`` (default 13, typical 2-50). Period 13 confirms trend; a very
        short period (around 2) makes a sensitive pullback oscillator; 20+ emphasizes
        longer-term force. Shorter is faster but noisier.

    Interpretation:
        Positive and rising indicates building buying force; negative and falling
        indicates building selling force. Zero-line crossovers mark momentum shifts, and
        price/force divergence warns of weakness. Pitfall: short periods whip around, so
        the smoothing length sets the signal's character.

    Outputs:
        force_index -- EMA of (close change * volume); positive for buyers, negative for
            sellers.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Elder, Trading for a Living (1993); pandas-ta (Elder's Force Index).
    """

    name = "force_index"
    outputs = ("force_index",)
    primary_param = "period"

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=13, ge=1)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("close", "volume"))
        raw = df["close"].diff() * df["volume"]
        return build_output(df.index, {"force_index": ema(raw, self.params["period"])})
