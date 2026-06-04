"""TTM Squeeze Pro (John Carter) — three-tier Bollinger-inside-Keltner squeeze + momentum.

The Squeeze fires when Bollinger Bands contract *inside* Keltner Channels (low volatility,
energy building). "Pro" grades that contraction at three Keltner widths — wide / normal /
narrow — via descending scalars (2.0 > 1.5 > 1.0), plus an "off" (BB outside the wide KC)
and "no squeeze" state. The momentum histogram is ``SMA(MOM(close, mom_length), mom_smooth)``
where ``MOM`` is the simple price change ``close.diff(mom_length)``.

Bollinger uses ``base.sma`` + population ``base.stdev`` (ddof=0); the Keltner band is
``scalar * base.sma(true_range)`` around an ``base.sma(close)`` basis (the pandas-ta ``kc``
``mamode="sma"``, ``tr=True`` convention — NOT the modern ATR/EMA Keltner). The squeeze flags
are pure band comparisons: NaN warm-up comparisons collapse to ``False``, so during warm-up
``sqz_no`` is 1 and the rest are 0 (matching pandas-ta's ``asint`` cast), while the momentum
column carries its own ``mom_length + mom_smooth - 1`` warm-up NaNs.

Best settings: defaults (bb 20/2.0, kc 20, scalars 2.0/1.5/1.0, mom 12/6) per Carter.
Edge cases: flat/zero-range window -> BB and KC collapse onto the basis, so neither
``BB_low > KC_low`` nor ``BB_low < KC_low`` holds -> ``sqz_no`` = 1 (no false squeeze).
Parity: pandas_ta_classic ``squeeze_pro`` default columns (mamode="sma", tr=True, asint=True).
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, model_validator

from pyindicators.base import sma, stdev, true_range
from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def _kc_bands(
    df: pd.DataFrame, length: int, scalar: float
) -> tuple[pd.Series, pd.Series]:
    """pandas-ta ``kc`` (mamode='sma', tr=True): (lower, upper) around an SMA(close) basis.

    pandas-ta's ``true_range`` leaves bar 0 as NaN (no prior close), so its SMA(TR) — and
    thus the KC bands — warm up one bar later than ``base.true_range`` (which falls back to
    H-L on bar 0). Blank bar 0 to keep that exact warm-up boundary, else the first defined
    KC bar diverges from the reference.
    """
    tr = true_range(df).copy()
    tr.iloc[0] = float("nan")
    basis = sma(df[CLOSE], length)
    band = scalar * sma(tr, length)
    return basis - band, basis + band


def squeeze_pro(
    df: pd.DataFrame,
    bb_length: int = 20,
    bb_std: float = 2.0,
    kc_length: int = 20,
    kc_scalar_wide: float = 2.0,
    kc_scalar_normal: float = 1.5,
    kc_scalar_narrow: float = 1.0,
    mom_length: int = 12,
    mom_smooth: int = 6,
) -> dict:
    """TTM Squeeze Pro: momentum histogram + wide/normal/narrow squeeze-on, off, no flags."""
    close = df[CLOSE]

    # Bollinger Bands (SMA basis + population stdev), only lower/upper are needed.
    bb_mid = sma(close, bb_length)
    bb_dev = bb_std * stdev(close, bb_length, ddof=0)
    bb_low, bb_high = bb_mid - bb_dev, bb_mid + bb_dev

    # Keltner Channels at three widths (pandas-ta sma/tr convention).
    kc_low_wide, kc_high_wide = _kc_bands(df, kc_length, kc_scalar_wide)
    kc_low_normal, kc_high_normal = _kc_bands(df, kc_length, kc_scalar_normal)
    kc_low_narrow, kc_high_narrow = _kc_bands(df, kc_length, kc_scalar_narrow)

    # Momentum histogram: SMA of the raw price change (pandas-ta mom = close.diff(length)).
    momentum = sma(close.diff(mom_length), mom_smooth)

    # Squeeze classification. Comparisons against warm-up NaNs yield False, so the flags are
    # 0/1 everywhere (never NaN) and warm-up resolves to sqz_no = 1 — matching pandas-ta asint.
    on_wide = (bb_low > kc_low_wide) & (bb_high < kc_high_wide)
    on_normal = (bb_low > kc_low_normal) & (bb_high < kc_high_normal)
    on_narrow = (bb_low > kc_low_narrow) & (bb_high < kc_high_narrow)
    off_wide = (bb_low < kc_low_wide) & (bb_high > kc_high_wide)
    no_squeeze = ~on_wide & ~off_wide

    return {
        "sqz": momentum,
        "sqz_on_wide": on_wide.astype("float64"),
        "sqz_on_normal": on_normal.astype("float64"),
        "sqz_on_narrow": on_narrow.astype("float64"),
        "sqz_off": off_wide.astype("float64"),
        "sqz_no": no_squeeze.astype("float64"),
    }


@INDICATORS.register
class SqueezePro(Indicator):
    """TTM Squeeze Pro.

    What: three-tier Bollinger-inside-Keltner squeeze (wide/normal/narrow) plus an SMA-smoothed
    momentum histogram — John Carter's extended TTM Squeeze.
    Best settings: bb 20/2.0, kc 20 with scalars 2.0/1.5/1.0, momentum 12 smoothed by 6.
    Edge cases: warm-up -> sqz_no = 1, others 0; flat/zero-range window -> sqz_no = 1 (no
    false squeeze); momentum NaN for the first ``mom_length + mom_smooth - 1`` bars.
    Parity: pandas_ta_classic ``squeeze_pro`` (mamode="sma", tr=True, asint=True) default columns.
    """

    spec = IndicatorSpec(
        name="squeeze_pro",
        category="momentum",
        aliases=("TTM Squeeze Pro", "SQZPRO"),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("sqz", "sqz_on_wide", "sqz_on_normal", "sqz_on_narrow", "sqz_off", "sqz_no"),
        bounds={
            "sqz_on_wide": (0.0, 1.0),
            "sqz_on_normal": (0.0, 1.0),
            "sqz_on_narrow": (0.0, 1.0),
            "sqz_off": (0.0, 1.0),
            "sqz_no": (0.0, 1.0),
        },
        references=("Carter", "pandas-ta squeeze_pro", "TradingView Squeeze PRO"),
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        bb_length: int = Field(default=20, ge=1)
        bb_std: float = Field(default=2.0, gt=0)
        kc_length: int = Field(default=20, ge=1)
        kc_scalar_wide: float = Field(default=2.0, gt=0)
        kc_scalar_normal: float = Field(default=1.5, gt=0)
        kc_scalar_narrow: float = Field(default=1.0, gt=0)
        mom_length: int = Field(default=12, ge=1)
        mom_smooth: int = Field(default=6, ge=1)

        @model_validator(mode="after")
        def _scalars_descending(self) -> SqueezePro.Params:
            if not (self.kc_scalar_wide > self.kc_scalar_normal > self.kc_scalar_narrow):
                raise ValueError(
                    "kc scalars must be strictly descending: "
                    "kc_scalar_wide > kc_scalar_normal > kc_scalar_narrow"
                )
            return self

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return squeeze_pro(
            df,
            bb_length=p["bb_length"],
            bb_std=p["bb_std"],
            kc_length=p["kc_length"],
            kc_scalar_wide=p["kc_scalar_wide"],
            kc_scalar_normal=p["kc_scalar_normal"],
            kc_scalar_narrow=p["kc_scalar_narrow"],
            mom_length=p["mom_length"],
            mom_smooth=p["mom_smooth"],
        )
