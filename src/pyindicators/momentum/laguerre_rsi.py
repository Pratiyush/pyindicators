"""Laguerre RSI — low-lag RSI on a 4-stage Laguerre filter (John Ehlers).

Ehlers replaces the moving-average smoothing of a classic RSI with a four-stage Laguerre
polynomial filter (L0..L3, a cascade of ``gamma``-weighted recursions). The RSI-style ratio
then compares the successive stage differences: cumulative "up" pressure ``CU`` (where an
earlier stage leads a later one) against "down" pressure ``CD``. A small ``gamma`` tracks
price tightly (more responsive, noisier); a large ``gamma`` adds lag and smoothing. The
result is bounded [0, 1] (the canonical Ehlers scale; TradingView/pandas-ta report 0..100,
i.e. ``100 * laguerre_rsi``). Stateful recursion seeded with the first close. See
``https://www.mesasoftware.com/papers/LaguerreFilters.pdf``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide


def laguerre_rsi(close: pd.Series, gamma: float = 0.5) -> pd.Series:
    """Ehlers Laguerre RSI of ``close`` for filter coefficient ``gamma``, bounded [0, 1].

    The four Laguerre stages are the standard cascade::

        L0 = (1 - gamma) * close + gamma * L0[-1]
        L1 = -gamma * L0 + L0[-1] + gamma * L1[-1]
        L2 = -gamma * L1 + L1[-1] + gamma * L2[-1]
        L3 = -gamma * L2 + L2[-1] + gamma * L3[-1]

    with all four seeded at ``close[0]``. ``CU``/``CD`` accumulate the positive/negative parts
    of the successive stage gaps (L0-L1, L1-L2, L2-L3); the RSI is ``CU / (CU + CD)``. A flat
    cascade (``CU + CD == 0``, e.g. a constant series or the seed bar) carries no directional
    pressure and is reported as 0.0 (Ehlers / pandas-ta convention), not NaN.
    """
    arr = close.to_numpy(dtype="float64")
    n = arr.size
    if n == 0:
        return pd.Series(np.empty(0, dtype="float64"), index=close.index)

    lag0 = np.empty(n, dtype="float64")
    lag1 = np.empty(n, dtype="float64")
    lag2 = np.empty(n, dtype="float64")
    lag3 = np.empty(n, dtype="float64")
    lag0[0] = lag1[0] = lag2[0] = lag3[0] = arr[0]
    for i in range(1, n):
        lag0[i] = (1.0 - gamma) * arr[i] + gamma * lag0[i - 1]
        lag1[i] = -gamma * lag0[i] + lag0[i - 1] + gamma * lag1[i - 1]
        lag2[i] = -gamma * lag1[i] + lag1[i - 1] + gamma * lag2[i - 1]
        lag3[i] = -gamma * lag2[i] + lag2[i - 1] + gamma * lag3[i - 1]

    d01 = lag0 - lag1
    d12 = lag1 - lag2
    d23 = lag2 - lag3
    cu = np.maximum(d01, 0.0) + np.maximum(d12, 0.0) + np.maximum(d23, 0.0)
    cd = np.maximum(-d01, 0.0) + np.maximum(-d12, 0.0) + np.maximum(-d23, 0.0)
    cu_s = pd.Series(cu, index=close.index)
    den = pd.Series(cu + cd, index=close.index)
    # den == 0 (flat cascade) -> 0.0: no up/down pressure, matches Ehlers & pandas-ta.
    return safe_divide(cu_s, den, fill=0.0)


@INDICATORS.register
class LaguerreRSI(Indicator):
    """Laguerre RSI.

    What: Ehlers' low-lag RSI computed on a 4-stage Laguerre filter rather than a moving
        average, giving earlier, smoother turns than Wilder's RSI.
    Best settings: ``gamma`` 0.5; lower (~0.2-0.4) for faster signals, higher (~0.7-0.8) for
        smoother, more lagging output. Bands at 0.2 / 0.8 (or 20 / 80 on the *100 scale).
    Edge cases: a flat cascade (constant series, or the seed bar) has CU+CD == 0 and is
        reported as 0.0; pure uptrend -> 1.0, pure downtrend -> 0.0.
    Parity: pandas-ta ``lrsi`` (which reports ``100 * laguerre_rsi``); identical L0..L3
        recursion, so exact up to the 1/100 scale.
    """

    spec = IndicatorSpec(
        name="laguerre_rsi",
        category="momentum",
        aliases=("Laguerre RSI", "LRSI", "Ehlers Laguerre RSI"),
        inputs=(CLOSE,),
        outputs=("laguerre_rsi",),
        bounds={"laguerre_rsi": (0.0, 1.0)},
        stateful=True,
        references=("Ehlers Laguerre Filters", "pandas-ta lrsi"),
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        gamma: float = Field(default=0.5, gt=0.0, lt=1.0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return laguerre_rsi(df[CLOSE], self.params["gamma"])
