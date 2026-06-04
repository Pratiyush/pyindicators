"""RSI Negative Reversal — Cardwell's bearish reversal pattern (Andrew Cardwell).

The bearish mirror of the positive reversal. In Cardwell's framework a *negative reversal*
fires when momentum and price disagree at successive RSI peaks: RSI carves a **lower high**
while price simultaneously carves a **higher high**. That hidden weakness (price up, momentum
down) typically resolves *downward*, so it is a bearish continuation/reversal signal.

Detection is a two-step, strictly causal process:

1.  Find RSI **local highs** (peaks): a bar whose RSI strictly exceeds its ``width`` neighbours
    on each side. A peak at bar ``t`` cannot be known until bar ``t + width`` has printed, so
    the flag is emitted at that **confirmation bar** — never on the peak bar itself (which would
    require looking ``width`` bars into the future). This keeps the indicator causal.
2.  Compare each confirmed RSI peak with the immediately preceding confirmed RSI peak. If the
    new RSI peak is **lower** *and* the bar ``high`` at the new peak is **higher**, set the flag
    to 1 on the confirmation bar.

Output ``rsi_negative_reversal`` is 0/1. Composes ``momentum.rsi`` (Wilder RMA). No reference
library implements Cardwell reversals, so it is validated against the explicit rule above.
See ``ref/ta_docs/momentum/RSI.md`` for the underlying RSI.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, HIGH, INDICATORS, Indicator, IndicatorSpec
from pyindicators.momentum.rsi import rsi


def rsi_negative_reversal(
    high: pd.Series,
    close: pd.Series,
    length: int = 14,
    width: int = 1,
) -> pd.Series:
    """Cardwell RSI negative-reversal flag (0/1), bearish.

    A confirmed RSI peak that is a *lower high* than the prior RSI peak while its bar ``high``
    is a *higher high* -> 1, emitted on the bar that confirms the peak (peak bar + ``width``).
    All other bars (and warm-up) -> 0. Strictly causal: confirmation needs ``width`` bars of
    right-hand context, so the flag never references future data relative to its own bar.
    """
    rsi_vals = rsi(close, length).to_numpy(dtype="float64")
    high_vals = high.to_numpy(dtype="float64")
    n = rsi_vals.size
    flag = np.zeros(n, dtype="float64")

    prev_peak_rsi = np.nan  # RSI value at the previous confirmed peak
    prev_peak_high = np.nan  # bar high at the previous confirmed peak
    # A peak sits at bar t (width <= t <= n-1-width). It is confirmed at bar t+width, which is
    # where we may legally write the flag. Iterate confirmation bars in time order.
    for t in range(width, n - width):
        centre = rsi_vals[t]
        if np.isnan(centre):
            continue
        left = rsi_vals[t - width : t]
        right = rsi_vals[t + 1 : t + 1 + width]
        if np.isnan(left).any() or np.isnan(right).any():
            continue
        if not ((centre > left).all() and (centre > right).all()):
            continue  # not a strict local high

        peak_high = high_vals[t]
        if not np.isnan(prev_peak_rsi):
            # Bearish: momentum makes a lower high while price makes a higher high.
            if centre < prev_peak_rsi and peak_high > prev_peak_high:
                flag[t + width] = 1.0  # write on the confirmation bar (causal)
        prev_peak_rsi = centre
        prev_peak_high = peak_high

    return pd.Series(flag, index=close.index)


@INDICATORS.register
class RSINegativeReversal(Indicator):
    """RSI Negative Reversal (Cardwell).

    What: a 0/1 bearish flag set when a confirmed RSI peak is a *lower high* than the prior RSI
        peak while the bar ``high`` at that peak is a *higher high* (momentum/price divergence
        that typically resolves down).
    Best settings: RSI ``length`` 14 (Cardwell); ``width`` 1 (3-bar pivot) for daily swings —
        raise ``width`` to demand wider, more significant RSI peaks.
    Edge cases: emitted on the peak's confirmation bar (peak + ``width``) so it is strictly
        causal; the first detectable peak only seeds state (no prior peak to compare), so it
        never flags; flat/warm-up regions -> 0.
    Parity: no reference-library implementation exists (TA-Lib/pandas-ta/finta/ta lack Cardwell
        reversals); validated against the explicit lower-high / higher-high rule above.
    """

    spec = IndicatorSpec(
        name="rsi_negative_reversal",
        category="momentum",
        aliases=("Cardwell Negative Reversal", "RSI Negative Reversal"),
        inputs=(HIGH, CLOSE),
        outputs=("rsi_negative_reversal",),
        bounds={"rsi_negative_reversal": (0.0, 1.0)},
        references=("Cardwell", "Brown 2012 Technical Analysis for the Trading Professional"),
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)
        width: int = Field(default=1, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        p = self.params
        return rsi_negative_reversal(df[HIGH], df[CLOSE], p["length"], p["width"])
