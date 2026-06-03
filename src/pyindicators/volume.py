"""Volume indicators: OBV, VWAP, relative volume, volume SMA, MFI.

Canonical definitions: OBV (Granville 1963), MFI (Quong & Soudack), VWAP (standard
execution metric), relative volume (IBD/O'Neil usage). All trailing-only (causal).
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
    """On-Balance Volume: running signed-volume total (starts at 0)."""

    name = "obv"
    outputs = ("obv",)

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        require_columns(df, ("close", "volume"))
        direction = np.sign(df["close"].diff().fillna(0.0))
        obv = (direction * df["volume"]).cumsum()
        return build_output(df.index, {"obv": obv})


@INDICATORS.register("vwap")
class VWAP(Indicator):
    """Volume-weighted average price.

    ``cumulative`` anchors from the start of the frame; ``session`` anchoring needs a
    calendar (intraday) and is not yet implemented, so it falls back to cumulative.
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
    """Relative volume: current volume / its trailing average."""

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
    """Simple moving average of volume."""

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
    """Money Flow Index: volume-weighted RSI on typical price, bounded [0, 100]."""

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
    """Elder's Force Index: EMA of (close change * volume). Period 2 = pullback oscillator,
    13 = trend. Positive = buyers in control, negative = sellers."""

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
