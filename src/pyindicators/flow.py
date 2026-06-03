"""Money-flow / volume-flow indicators: ADL, Chaikin Money Flow, Williams A/D.

This module bundles the accumulation/distribution family that gauges buying versus
selling pressure from where price closes inside each bar's range. The Accumulation/
Distribution Line (Marc Chaikin) and Chaikin Money Flow (Chaikin) weight that close
location by volume; the Accumulation/Distribution Line is a running cumulative total
while Chaikin Money Flow normalizes it over a window into a bounded [-1, 1] oscillator.
Williams Accumulation/Distribution (Larry Williams) is a volume-free cumulative line
driven by close-to-close direction. All are trailing-only (causal): every value uses
current and prior bars only, never future data.

Sources: Accumulation/Distribution Line (Marc Chaikin); Chaikin Money Flow (Chaikin);
Williams Accumulation/Distribution (Larry Williams). All trailing-only (causal).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from .base import Indicator
from .common import build_output, require_columns
from .registry import INDICATORS


def _money_flow_volume(df: pd.DataFrame) -> pd.Series:
    """Chaikin money-flow volume: ((C-L)-(H-C))/(H-L) * volume; 0 where H==L."""
    hl = df["high"] - df["low"]
    mfm = ((df["close"] - df["low"]) - (df["high"] - df["close"])) / hl
    mfm = mfm.where(hl != 0, 0.0)  # no range -> no money-flow signal
    return mfm * df["volume"]


@INDICATORS.register("adl")
class AccumulationDistributionLine(Indicator):
    """Accumulation/Distribution Line: cumulative running total of money-flow volume.

    What it is:
        A cumulative, volume-based money-flow indicator that measures the flow of money
        into and out of a security to assess accumulation versus distribution pressure.
        Developed by Marc Chaikin.

    How it works:
        For each bar, the Money Flow Multiplier (MFM) = ((Close - Low) - (High - Close))
        / (High - Low), which ranges from +1 (close at the high, buying pressure) to -1
        (close at the low, selling pressure). Money Flow Volume = MFM times volume, and
        the line is the running sum of that money-flow volume. A zero-range bar (High ==
        Low) contributes nothing.

    Best settings:
        No parameters. Reads off any timeframe. The absolute level is arbitrary and
        depends on the start point, so interpret the line by its slope and divergences,
        not its raw value.

    Interpretation:
        Rising line with rising price confirms an uptrend (accumulation); rising line
        with falling price signals underlying buying (bullish divergence); falling line
        with rising price warns of a weakening trend (bearish divergence). Pitfall: the
        level itself is meaningless; only direction and divergences matter.

    Outputs:
        adl -- cumulative money-flow volume; rises on accumulation, falls on distribution.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Chaikin, Accumulation/Distribution Line; StockCharts ChartSchool.
    """

    name = "adl"
    outputs = ("adl",)

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("high", "low", "close", "volume"))
        return build_output(df.index, {"adl": _money_flow_volume(df).cumsum()})


@INDICATORS.register("cmf")
class ChaikinMoneyFlow(Indicator):
    """Chaikin Money Flow: windowed money-flow volume over volume, bounded [-1, 1].

    What it is:
        A volume-weighted oscillator that measures money-flow intensity by combining the
        Money Flow Multiplier (where price closes inside its range) with volume over a
        lookback window. Created by Marc Chaikin; oscillates between -1 and +1.

    How it works:
        For each bar, Money Flow Volume = ((Close - Low) - (High - Close)) / (High - Low)
        times volume. CMF = sum of money-flow volume over N periods divided by the sum of
        volume over the same N periods. The result is bounded -1 to +1 and typically sits
        between -0.5 and +0.5; a window with zero total volume is left undefined (NaN).

    Best settings:
        Default period is 20 (20 or 21 is standard); typical range is 10-30. Use a
        shorter period (10) for a faster, more sensitive response and a longer one (30)
        for broader trend confirmation.

    Interpretation:
        Values above 0 indicate buying pressure, below 0 selling pressure; readings beyond
        +0.25 or -0.25 suggest strong directional pressure. A zero-line cross signals a
        trend change. Pitfall: price-versus-CMF divergence can warn of a weakening trend.

    Outputs:
        cmf -- money-flow ratio in [-1, 1]; positive is net buying, negative net selling.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Chaikin, Chaikin Money Flow; StockCharts ChartSchool.
    """

    name = "cmf"
    outputs = ("cmf",)
    primary_param = "period"
    bounds = {"cmf": (-1.0, 1.0)}

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=20, ge=1)

    params_model = Params

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("high", "low", "close", "volume"))
        p = self.params["period"]
        mfv = _money_flow_volume(df).rolling(p, min_periods=p).sum()
        vol = df["volume"].rolling(p, min_periods=p).sum()
        with np.errstate(divide="ignore", invalid="ignore"):
            cmf = mfv / vol  # zero-volume window -> NaN (not inf)
        return build_output(df.index, {"cmf": cmf.where(vol != 0)})


@INDICATORS.register("williams_ad")
class WilliamsAD(Indicator):
    """Williams Accumulation/Distribution: volume-free cumulative A/D from close direction.

    What it is:
        A cumulative accumulation/distribution line that gauges buying versus selling
        pressure from close-to-close direction and the true range, without using volume.
        Developed by Larry Williams.

    How it works:
        Each bar's contribution depends on the close versus the prior close. On an up
        close, add the close minus the lower of the current low and the prior close
        (true-range low); on a down close, add the close minus the higher of the current
        high and the prior close (true-range high); on an unchanged close, add nothing.
        The line is the running sum of those daily contributions, with the first bar (no
        prior close) contributing zero.

    Best settings:
        No parameters. Reads off any timeframe. The absolute level depends on the start
        point, so read the line by its slope and divergences rather than its raw value.

    Interpretation:
        A rising line reflects accumulation (buying pressure); a falling line reflects
        distribution (selling pressure). Divergence between the line and price can signal
        an impending reversal. Pitfall: the level itself is meaningless; only direction
        and divergences carry information.

    Outputs:
        williams_ad -- cumulative accumulation/distribution; rises on accumulation, falls
            on distribution.

    Causal: trailing-only; no look-ahead. Warm-up rows are NaN until the window fills.
    Source: Larry Williams, Accumulation/Distribution.
    """

    name = "williams_ad"
    outputs = ("williams_ad",)

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("high", "low", "close"))
        close = df["close"]
        prev = close.shift(1)
        up = close - np.minimum(df["low"], prev)
        down = close - np.maximum(df["high"], prev)
        ad = np.where(close > prev, up, np.where(close < prev, down, 0.0))
        ad = pd.Series(ad, index=df.index).fillna(0.0)  # first bar (no prev) contributes 0
        return build_output(df.index, {"williams_ad": ad.cumsum()})
