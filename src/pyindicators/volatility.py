"""Volatility indicators: ATR, Bollinger Bands, Keltner Channels, rolling std.

Canonical definitions: ATR (Wilder 1978), Bollinger Bands (Bollinger),
Keltner Channels (Keltner). All trailing-only (causal).
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from .base import Indicator
from .common import build_output, ema, require_columns, true_range, wilder_rma
from .registry import INDICATORS


@INDICATORS.register("atr")
class ATR(Indicator):
    """Average True Range (Wilder). Emits both ATR and the raw True Range."""

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
    """Bollinger Bands: SMA mid +/- ``num_std`` population std, plus width and %B."""

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
    """Keltner Channels: EMA mid +/- ``mult`` * ATR."""

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
    """Rolling population standard deviation of close."""

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
    """TTM Squeeze (Carter): Bollinger Bands inside Keltner Channels.

    ``ttm_squeeze`` is 1.0 while volatility is compressed (BBs inside KCs) and 0.0 once it
    expands ("fires"); ``ttm_momentum`` is a close-minus-midline momentum proxy.
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
