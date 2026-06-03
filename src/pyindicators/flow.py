"""Money-flow / accumulation indicators: ADL, Chaikin Money Flow, Williams A/D.

Sources: Accumulation/Distribution Line (Chaikin); Chaikin Money Flow (Chaikin);
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
    """Accumulation/Distribution Line: running total of money-flow volume."""

    name = "adl"
    outputs = ("adl",)

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("high", "low", "close", "volume"))
        return build_output(df.index, {"adl": _money_flow_volume(df).cumsum()})


@INDICATORS.register("cmf")
class ChaikinMoneyFlow(Indicator):
    """Chaikin Money Flow: money-flow volume / volume over a window, bounded [-1, 1]."""

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
    """Williams Accumulation/Distribution: volume-free, true-range-based cumulative A/D."""

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
