"""RSI Positive Reversal — Andrew Cardwell's bullish reversal signal.

Cardwell's "positive reversal": at a swing low the oscillator and price disagree in the
*bullish* direction. Concretely, between two consecutive RSI troughs the RSI trough rises
(``RSI`` makes a HIGHER low) while price at those same bars falls (``low`` makes a LOWER
low). That hidden strength — buyers stepping in even as price probes lower — is read as a
continuation-of-uptrend / bullish signal and flagged ``1`` (otherwise ``0``).

Trough detection is a strict 3-bar local minimum on ``rsi(close, length)``: bar ``t`` is a
trough when ``RSI[t-1] > RSI[t] < RSI[t+1]``. A trough is only *knowable* one bar later, so
the flag is emitted at the CONFIRMATION bar ``t+1`` using exclusively rows ``<= t+1`` — the
indicator is therefore strictly causal (no look-ahead). Composes ``momentum.rsi``. There is
no reference-library oracle; the explicit rule is golden-tested. See Cardwell / Constance
Brown, *Technical Analysis for the Trading Professional*.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, LOW, Indicator, IndicatorSpec
from pyindicators.momentum.rsi import rsi


def rsi_positive_reversal(
    low: pd.Series,
    close: pd.Series,
    length: int = 14,
) -> pd.Series:
    """Cardwell RSI positive-reversal flag (0/1) emitted at each trough's confirmation bar.

    A strict 3-bar RSI trough at bar ``t`` (``RSI[t-1] > RSI[t] < RSI[t+1]``) is compared to
    the previous RSI trough ``p``: a positive reversal fires when ``RSI[t] > RSI[p]`` (higher
    RSI low) AND ``low[t] < low[p]`` (lower price low). The flag is written to the next bar
    ``t+1`` (the first bar that confirms ``t`` was a pivot), keeping the signal causal.
    """
    r = rsi(close, length).to_numpy(dtype="float64")
    lows = low.to_numpy(dtype="float64")
    n = r.size
    out = np.zeros(n, dtype="float64")

    prev_t = -1  # index of the most recent confirmed RSI trough (-1 = none yet)
    # Scan trough candidates t in [1, n-2]; confirmation requires the t+1 bar to exist.
    for t in range(1, n - 1):
        rm1, r0, rp1 = r[t - 1], r[t], r[t + 1]
        if not (np.isfinite(rm1) and np.isfinite(r0) and np.isfinite(rp1)):
            continue
        if not (rm1 > r0 < rp1):  # strict local minimum in RSI
            continue
        if prev_t >= 0:
            rsi_higher_low = r0 > r[prev_t]
            price_lower_low = lows[t] < lows[prev_t]
            if rsi_higher_low and price_lower_low:
                out[t + 1] = 1.0  # emit at the confirmation bar -> strictly causal
        prev_t = t
    return pd.Series(out, index=close.index)


@INDICATORS.register
class RSIPositiveReversal(Indicator):
    """RSI Positive Reversal (Cardwell).

    What: a bullish signal where, between two RSI troughs, RSI makes a higher low while price
        makes a lower low — hidden accumulation inside an uptrend. Flagged 1 at the bar that
        confirms the second trough, else 0.
    Best settings: ``length`` 14 (Wilder RSI); read in the context of an established uptrend.
    Edge cases: needs two detectable 3-bar RSI troughs before any signal can fire (the first
        trough only sets the baseline); flat/warm-up RSI yields 0; output is always finite.
    Parity: no reference-library oracle exists (Cardwell reversals are not in TA-Lib /
        pandas-ta / finta / ta) — the explicit rule is golden- and oracle-tested instead.
    """

    spec = IndicatorSpec(
        name="rsi_positive_reversal",
        category="momentum",
        aliases=("Cardwell Positive Reversal", "RSI Positive Reversal"),
        inputs=(LOW, CLOSE),
        outputs=("rsi_positive_reversal",),
        bounds={"rsi_positive_reversal": (0.0, 1.0)},
        causal=True,  # flag emitted at the trough's confirmation bar -> uses only rows <= i
        references=("Cardwell positive reversal", "Constance Brown TA for the Trading Pro"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return rsi_positive_reversal(df[LOW], df[CLOSE], self.params["length"])
