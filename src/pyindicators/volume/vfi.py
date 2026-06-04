"""VFI — Volume Flow Indicator (Markos Katsanos, TASC June/July 2004).

An OBV-style money-flow gauge that only counts a bar's volume when the typical-price move is
large enough to matter. Each bar's *typical price* (HLC3) change is compared to a volatility
``cutoff = factor * stdev(log-typical-change, 30) * close``: moves above ``+cutoff`` add volume,
moves below ``-cutoff`` subtract it, and small moves contribute nothing. Volume is first capped
at ``vfactor * SMA(volume, period)`` so a single spike cannot dominate, the signed/capped volume
is summed over ``period`` and normalised by average volume, then smoothed by a short EMA.

Composes ``base.stdev`` (sample ddof=1, for the log-return volatility) and ``core.safe_divide``
(guards the average-volume normaliser). The final smoother is pandas' *adjusted* EWM
(``span=smoothing, adjust=True``), which is a different convention from ``base.ema`` (TA-Lib
SMA-seeded, adjust=False); it is inlined here so the result matches finta bit-for-bit.

Parity: finta ``TA.VFI`` (exact, 0.0 max-abs diff on deterministic and real frames). NOTE:
``pandas_ta_classic.vfi`` ships a *different, degenerate* formula (cutoff = ``coef*close`` with no
stdev and no volume sign) that returns all-zeros on normal daily data, so finta is the oracle.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import stdev
from pyindicators.core import (
    CLOSE,
    HIGH,
    INDICATORS,
    LOW,
    VOLUME,
    Indicator,
    IndicatorSpec,
    safe_divide,
)


def vfi(
    df: pd.DataFrame,
    period: int = 130,
    smoothing: int = 3,
    factor: float = 0.2,
    vfactor: float = 2.5,
) -> pd.Series:
    """Volume Flow Indicator over ``period`` bars, smoothed by an ``smoothing``-span EMA.

    Steps (causal, all trailing windows): typical price HLC3 -> volatility ``cutoff`` from the
    30-bar sample stdev of its log change -> per-bar sign (+1/-1/0) by typical-price change vs
    ``+/-cutoff`` -> volume capped at ``vfactor * SMA(volume, period)`` -> ``period``-sum of
    signed capped volume, divided by the prior bar's average volume -> adjusted EWM smoother.
    """
    typical = (df[HIGH] + df[LOW] + df[CLOSE]) / 3.0
    # Volatility cutoff from the sample stdev (ddof=1) of the log typical-price change.
    log_change = np.log(typical).diff()
    cutoff = factor * stdev(log_change, 30, ddof=1) * df[CLOSE]

    price_change = typical.diff()
    mav = df[VOLUME].rolling(period, min_periods=period).mean()
    mav_prev = mav.shift(1)  # prior-bar average volume (finta uses mav.shift())

    # Cap each bar's volume at vfactor * prior-average; where the cap is NaN (warm-up) the
    # bar's own volume is kept (matches finta's `volume > vfactor*mav` test, NaN -> False).
    vmax = vfactor * mav_prev
    capped_vol = df[VOLUME].where(~(df[VOLUME] > vmax), vmax)

    # Sign the volume; finta zero-fills price_change/cutoff before the +/-cutoff comparison so
    # warm-up bars score 0 rather than NaN.
    pc = price_change.fillna(0.0)
    cut = cutoff.fillna(0.0)
    multiplier = pd.Series(0.0, index=df.index)
    multiplier[pc > cut] = 1.0
    multiplier[pc < -cut] = -1.0

    raw_sum = (multiplier * capped_vol).rolling(period, min_periods=period).sum()
    raw_value = safe_divide(raw_sum, mav_prev)  # guard zero average volume -> NaN

    # Adjusted EWM (pandas convention, NOT base.ema) for exact finta parity.
    return raw_value.ewm(span=smoothing, min_periods=smoothing - 1, adjust=True).mean()


@INDICATORS.register
class VFI(Indicator):
    """Volume Flow Indicator (Katsanos).

    What: OBV-like flow that only sums volume on typical-price moves bigger than a volatility
    cutoff, with volume capped to tame spikes, then EWM-smoothed.
    Best settings: 130 / 3 / 0.2 / 2.5 (Katsanos daily); above zero = accumulation.
    Edge cases: flat typical price -> cutoff 0 and no qualifying move -> VFI 0; warm-up is
    ``period`` + 1 bars (rolling sum + the ``mav.shift``); zero average volume -> guarded NaN.
    Parity: finta ``TA.VFI`` (exact). ``pandas_ta_classic.vfi`` is a degenerate variant; not used.
    """

    spec = IndicatorSpec(
        name="vfi",
        category="volume",
        aliases=("Volume Flow Indicator", "Katsanos VFI"),
        inputs=(HIGH, LOW, CLOSE, VOLUME),
        outputs=("vfi",),
        references=("Katsanos TASC 2004", "finta VFI"),
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=130, ge=2)
        smoothing: int = Field(default=3, ge=2)
        factor: float = Field(default=0.2, gt=0)
        vfactor: float = Field(default=2.5, gt=0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        p = self.params
        return vfi(df, p["period"], p["smoothing"], p["factor"], p["vfactor"])
