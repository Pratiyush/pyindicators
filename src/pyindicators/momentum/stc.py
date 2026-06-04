"""STC — Schaff Trend Cycle (Doug Schaff, 2008).

A faster, cleaner MACD: run a stochastic over the MACD line, smooth it, run a *second*
stochastic over that, and smooth again. The result is a 0-100 cycle that turns earlier and
whipsaws less than the raw MACD. Composes ``base.ema``. See ``ref/ta_docs/momentum/misc_momentum.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

_EPS = np.finfo(np.float64).eps


def _nz_range(s: pd.Series, length: int) -> tuple:
    """Rolling (low, high-low) with pandas-ta's non-zero-range epsilon guard."""
    low = s.rolling(length).min()
    rng = s.rolling(length).max() - low
    if bool((rng == 0).any()):
        rng = rng + _EPS
    return low.to_numpy(), rng.to_numpy()


def _stoch_smooth(src: np.ndarray, low: np.ndarray, rng: np.ndarray, factor: float,
                  gate_on_low: bool) -> tuple:
    """One Schaff stage: stochastic of ``src`` (carried forward when ungated) + EMA smoothing."""
    m = src.size
    stoch = np.zeros(m)
    pf = np.zeros(m)
    for i in range(1, m):
        gate = low[i] > 0 if gate_on_low else rng[i] > 0
        if gate:
            stoch[i] = 100.0 * (src[i] - low[i]) / rng[i]
        else:
            stoch[i] = stoch[i - 1]
        pf[i] = round(pf[i - 1] + factor * (stoch[i] - pf[i - 1]), 8)
    return stoch, pf


def stc(
    close: pd.Series,
    tclength: int = 10,
    fast: int = 12,
    slow: int = 26,
    factor: float = 0.5,
) -> dict:
    """Schaff Trend Cycle, its MACD line, and the intermediate stochastic (0-100)."""
    xmacd = (ema(close, fast) - ema(close, slow))
    x = xmacd.to_numpy()
    low1, rng1 = _nz_range(xmacd, tclength)
    _, pf = _stoch_smooth(x, low1, rng1, factor, gate_on_low=True)  # 1st: MACD quirk gates on low
    pf_s = pd.Series(pf, index=close.index)
    low2, rng2 = _nz_range(pf_s, tclength)
    _, pff = _stoch_smooth(pf, low2, rng2, factor, gate_on_low=False)  # 2nd: gate on range
    return {
        "stc": pd.Series(pff, index=close.index),
        "stc_macd": xmacd,
        "stc_stoch": pf_s,
    }


@INDICATORS.register
class STC(Indicator):
    """Schaff Trend Cycle.

    What: a double-stochastic, double-smoothed MACD that cycles 0-100 with less lag/whipsaw.
    Best settings: tclength 10, fast 12, slow 26, factor 0.5; > 75 overbought, < 25 oversold.
    Edge cases: warm-up carries 0 until the stochastic windows fill; bounded 0-100.
    Parity: pandas-ta ``stc`` (STC/STCmacd/STCstoch); EMA-seeded, exact.
    """

    spec = IndicatorSpec(
        name="stc",
        category="momentum",
        aliases=("Schaff Trend Cycle",),
        inputs=(CLOSE,),
        outputs=("stc", "stc_macd", "stc_stoch"),
        bounds={"stc": (0.0, 100.0), "stc_stoch": (0.0, 100.0)},
        stateful=True,
        references=("Schaff 2008", "pandas-ta stc"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        tclength: int = Field(default=10, ge=1)
        fast: int = Field(default=12, ge=1)
        slow: int = Field(default=26, ge=1)
        factor: float = Field(default=0.5, gt=0.0, le=1.0)

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return stc(df[CLOSE], p["tclength"], p["fast"], p["slow"], p["factor"])
