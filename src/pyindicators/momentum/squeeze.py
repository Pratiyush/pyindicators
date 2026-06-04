"""TTM Squeeze (SQZ) — John Carter's Bollinger-inside-Keltner volatility regime + momentum.

Detects "squeezes": low-volatility coils where the Bollinger Bands contract *inside* the
Keltner Channels (a breakout setup), versus releases where they expand outside. Alongside the
on/off flags it carries a momentum oscillator that hints at the likely breakout direction.

This is the pandas-ta *default* mode (``lazybear=False``, ``mamode="sma"``, ``tr=True``):

- BB  = SMA(close, bb_length) +/- bb_std * population-stdev(close, bb_length)   (ddof=0)
- KC  = SMA(close, kc_length) +/- kc_scalar * SMA(TrueRange, kc_length)
- SQZ momentum = SMA( MOM(close, mom_length), mom_smooth )   where MOM = close.diff(n)
- squeeze_on  = (BB_lower > KC_lower) & (BB_upper < KC_upper)
- squeeze_off = (BB_lower < KC_lower) & (BB_upper > KC_upper)
- squeeze_no  = ~on & ~off   (also captures the warm-up window, where bands are NaN)

NOTE: the LazyBear TradingView variant (linreg of close minus the HH/LL/KC-mid average) is a
*different* momentum definition; we implement the pandas-ta default, not LazyBear.

Composes ``base.sma``, ``base.stdev``, ``base.true_range`` and ``momentum.mom`` — never
re-inlines the moving-average / stdev / true-range math.

Parity: pandas-ta ``squeeze`` default-mode columns (SQZ / SQZ_ON / SQZ_OFF / SQZ_NO).
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma, stdev, true_range
from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec

from .mom import mom


def squeeze(
    df: pd.DataFrame,
    bb_length: int = 20,
    bb_std: float = 2.0,
    kc_length: int = 20,
    kc_scalar: float = 1.5,
    mom_length: int = 12,
    mom_smooth: int = 6,
) -> dict:
    """TTM Squeeze (pandas-ta default mode): momentum + squeeze_on/off/no flags.

    Returns floats throughout; the on/off/no flags are 1.0/0.0 (a row is in exactly one of
    the three states). During warm-up the bands are NaN, the on/off comparisons are False, so
    ``squeeze_no`` is 1.0 there — matching pandas-ta, which casts the bool flags to int.
    """
    close = df[CLOSE]

    # Bollinger Bands on close: SMA basis +/- bb_std * population stdev (ddof=0).
    bb_mid = sma(close, bb_length)
    bb_dev = bb_std * stdev(close, bb_length, ddof=0)
    bb_lower = bb_mid - bb_dev
    bb_upper = bb_mid + bb_dev

    # Keltner Channels: SMA(close) basis +/- kc_scalar * SMA(TrueRange).
    kc_basis = sma(close, kc_length)
    kc_band = kc_scalar * sma(true_range(df), kc_length)
    kc_lower = kc_basis - kc_band
    kc_upper = kc_basis + kc_band

    # Momentum oscillator: smoothed price momentum (SMA of MOM).
    momentum = sma(mom(close, mom_length), mom_smooth)

    # Squeeze classification. NaN comparisons -> False, so warm-up lands in squeeze_no.
    on = (bb_lower > kc_lower) & (bb_upper < kc_upper)
    off = (bb_lower < kc_lower) & (bb_upper > kc_upper)
    no = ~on & ~off
    return {
        "squeeze": momentum,
        "squeeze_on": on.astype("float64"),
        "squeeze_off": off.astype("float64"),
        "squeeze_no": no.astype("float64"),
    }


@INDICATORS.register
class Squeeze(Indicator):
    """TTM Squeeze (SQZ).

    What: Bollinger-inside-Keltner volatility regime (on/off/no) plus a smoothed momentum
        oscillator that hints at breakout direction (John Carter, "Mastering the Trade").
    Best settings: BB 20/2.0, KC 20/1.5, momentum 12 smoothed by 6 (pandas-ta defaults).
    Edge cases: warm-up rows (bands still NaN) classify as ``squeeze_no`` = 1; a fully flat
        series collapses both envelopes so ``squeeze_on`` stays 0 (no false squeeze).
    Parity: pandas-ta ``squeeze`` default mode (lazybear=False, mamode="sma", tr=True);
        columns map to SQZ / SQZ_ON / SQZ_OFF / SQZ_NO.
    """

    spec = IndicatorSpec(
        name="squeeze",
        category="momentum",
        aliases=("TTM Squeeze", "SQZ", "Squeeze Momentum"),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("squeeze", "squeeze_on", "squeeze_off", "squeeze_no"),
        bounds={
            "squeeze_on": (0.0, 1.0),
            "squeeze_off": (0.0, 1.0),
            "squeeze_no": (0.0, 1.0),
        },
        references=("Carter Mastering the Trade", "pandas-ta squeeze"),
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        bb_length: int = Field(default=20, ge=1)
        bb_std: float = Field(default=2.0, gt=0)
        kc_length: int = Field(default=20, ge=1)
        kc_scalar: float = Field(default=1.5, gt=0)
        mom_length: int = Field(default=12, ge=1)
        mom_smooth: int = Field(default=6, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return squeeze(
            df,
            p["bb_length"],
            p["bb_std"],
            p["kc_length"],
            p["kc_scalar"],
            p["mom_length"],
            p["mom_smooth"],
        )
