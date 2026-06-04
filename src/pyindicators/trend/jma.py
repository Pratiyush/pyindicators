"""JMA — Jurik Moving Average (Mark Jurik).

A low-lag, very smooth adaptive average. Each bar measures price volatility against running
Jurik bands, normalises it into a relative-volatility factor, and uses that to drive a
three-stage filter: (1) an adaptive EMA, (2) a Kalman-style preliminary smoother whose gain
is the phase ratio ``pr``, and (3) Jurik's unique adaptive final filter. Stateful scalar
recursion seeded from the first close; the first ``length - 1`` bars are NaN warm-up. The
volatility average is a trailing 65-bar look-back, so the result is causal. Ports
``pandas_ta_classic.overlap.jma`` faithfully. See ``ref/ta_docs/trend/misc_MA.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def _phase_ratio(phase: float) -> float:
    """JMA phase -> PR smoothing coefficient (clamped): 0.5 below -100, 2.5 above 100."""
    if phase < -100.0:
        return 0.5
    if phase > 100.0:
        return 2.5
    return 1.5 + phase * 0.01


def jma(close: pd.Series, length: int = 7, phase: float = 0.0) -> pd.Series:
    """Jurik Moving Average over ``length`` bars with ``phase`` in [-100, 100].

    Three-stage adaptive filter (adaptive EMA -> Kalman pre-smooth -> Jurik final filter)
    driven by a relative-volatility factor from running Jurik bands. The first ``length - 1``
    bars are NaN (pandas-ta warm-up); a flat series gives zero volatility and the filter
    reduces to a steady EMA toward the constant.
    """
    x = close.to_numpy(dtype="float64")
    m = x.size
    out = np.zeros(m, dtype="float64")
    if m == 0:
        return pd.Series(out, index=close.index)

    volty = np.zeros(m, dtype="float64")
    v_sum = np.zeros(m, dtype="float64")

    det0 = det1 = ma2 = 0.0
    # Seed all three stages and both bands from the first close (pandas-ta convention).
    out[0] = ma1 = u_band = l_band = x[0]

    sum_length = 10
    half_len = 0.5 * (length - 1)
    pr = _phase_ratio(phase)
    # length=1 -> half_len 0 -> log(0) = -inf; the max() clamps length1 to 0 (same as pandas-ta).
    with np.errstate(divide="ignore"):
        length1 = max((np.log(np.sqrt(half_len)) / np.log(2.0)) + 2.0, 0.0)
    pow1 = max(length1 - 2.0, 0.5)
    length2 = length1 * np.sqrt(half_len)
    bet = length2 / (length2 + 1.0)
    beta = 0.45 * (length - 1) / (0.45 * (length - 1) + 2.0)

    for i in range(1, m):
        price = x[i]

        # Price volatility vs the two running bands.
        del1 = price - u_band
        del2 = price - l_band
        volty[i] = max(abs(del1), abs(del2)) if abs(del1) != abs(del2) else 0.0

        # Relative price-volatility factor over a trailing 65-bar window (causal look-back).
        v_sum[i] = v_sum[i - 1] + (volty[i] - volty[max(i - sum_length, 0)]) / sum_length
        avg_volty = np.average(v_sum[max(i - 65, 0) : i + 1])
        d_volty = 0.0 if avg_volty == 0 else volty[i] / avg_volty
        r_volty = max(1.0, min(np.power(length1, 1.0 / pow1), d_volty))

        # Jurik volatility bands.
        pow2 = np.power(r_volty, pow1)
        kv = np.power(bet, np.sqrt(pow2))
        u_band = price if (del1 > 0) else price - (kv * del1)
        l_band = price if (del2 < 0) else price - (kv * del2)

        # Jurik dynamic factor.
        power = np.power(r_volty, pow1)
        alpha = np.power(beta, power)

        # Stage 1 — adaptive EMA.
        ma1 = ((1.0 - alpha) * price) + (alpha * ma1)
        # Stage 2 — Kalman-style preliminary smoothing (gain = phase ratio).
        det0 = ((price - ma1) * (1.0 - beta)) + (beta * det0)
        ma2 = ma1 + pr * det0
        # Stage 3 — Jurik's unique adaptive final filter.
        det1 = ((ma2 - out[i - 1]) * (1.0 - alpha) * (1.0 - alpha)) + (alpha * alpha * det1)
        out[i] = out[i - 1] + det1

    out[0 : length - 1] = np.nan  # pandas-ta warm-up: first length-1 bars undefined
    return pd.Series(out, index=close.index)


@INDICATORS.register
class JMA(Indicator):
    """Jurik Moving Average.

    What: a low-lag, very smooth adaptive MA — a three-stage filter (adaptive EMA -> Kalman
        pre-smooth -> Jurik final filter) steered by a relative-volatility factor.
    Best settings: ``length`` 7 (Jurik default); ``phase`` -100..100 trades smoothness for
        responsiveness (0 is neutral).
    Edge cases: seeded from the first close; first ``length - 1`` bars NaN; a flat series
        collapses to a steady EMA toward the constant.
    Parity: pandas-ta ``jma`` (length=7, phase=0), exact recursion.
    """

    spec = IndicatorSpec(
        name="jma",
        category="trend",
        aliases=("Jurik Moving Average", "JMA"),
        inputs=(CLOSE,),
        outputs=("jma",),
        stateful=True,
        references=("Jurik", "pandas-ta jma"),
        doc="ref/ta_docs/trend/misc_MA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=7, ge=1)
        phase: float = Field(default=0.0, ge=-100.0, le=100.0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return jma(df[CLOSE], self.params["length"], self.params["phase"])
