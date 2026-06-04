"""SAREXT — Extended Parabolic SAR (TA-Lib SAREXT).

An extended Parabolic SAR that (a) allows independent acceleration settings for long vs short
legs, (b) supports a fixed ``start_value`` seed and a fractional ``offset_on_reverse`` nudge
applied when the system flips, and (c) **sign-encodes direction**: the output is the SAR value
itself while long, and the NEGATED SAR while short. With the default parameters it tracks the
plain Parabolic SAR but emits short-leg stops as negative numbers (the SAREXT convention).

Stateful recursion seeded from the first two bars' directional movement (Wilder/TA-Lib): the
first bar is NaN, the second is the seed stop, and each subsequent bar advances the stop by
``af * (EP - SAR)``, stepping ``af`` on every new extreme and clamping the stop out of the two
prior bars' range. Reverse-engineered to match ``talib.SAREXT`` exactly (the seed/reversal step
ordering differs from pandas-ta's pure-python port). See ``src/pyindicators/trend/psar.py`` for
the single-leg sibling.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def sarext(
    df: pd.DataFrame,
    start_value: float = 0.0,
    offset_on_reverse: float = 0.0,
    af_init_long: float = 0.02,
    af_long: float = 0.02,
    af_max_long: float = 0.2,
    af_init_short: float = 0.02,
    af_short: float = 0.02,
    af_max_short: float = 0.2,
) -> pd.Series:
    """Extended Parabolic SAR (signed): positive = long stop, negative = short stop.

    Mirrors ``talib.SAREXT``: first bar NaN; long/short legs carry independent acceleration
    factors; the stop jumps to the prior extreme on a flip (optionally nudged by
    ``offset_on_reverse``) and is clamped out of the two most recent bars' range.
    """
    high = df[HIGH].to_numpy(dtype="float64")
    low = df[LOW].to_numpy(dtype="float64")
    n = high.size
    out = np.full(n, np.nan)
    if n < 2:
        return pd.Series(out, index=df.index)

    # Initial trend: short if the first bar's -DM dominates +DM (Wilder/TA-Lib seed). A nonzero
    # start_value forces the side by its sign and seeds the stop at |start_value|.
    if start_value == 0.0:
        is_long = not ((low[0] - low[1]) > (high[1] - high[0]))
        sar = low[0] if is_long else high[0]
    else:
        is_long = start_value > 0.0
        sar = abs(start_value)
    ep = high[1] if is_long else low[1]
    af = af_init_long if is_long else af_init_short

    prev_high, prev_low = high[0], low[0]
    for row in range(1, n):
        hi, lo = high[row], low[row]
        # The prior-extreme clamp is skipped on the very first bar: there is only one prior bar,
        # so clamping against it would spuriously pin the stop to the seed (TA-Lib does not).
        first = row == 1
        if is_long:
            if lo <= sar:  # flip long -> short
                is_long = False
                sar = ep
                if offset_on_reverse != 0.0:
                    sar += sar * offset_on_reverse
                sar = max(sar, prev_high, hi)
                out[row] = -sar
                ep, af = lo, af_init_short
                sar = sar + af * (ep - sar)  # advance the new short leg one step
                sar = max(sar, prev_high, hi)
            else:
                out[row] = sar
                if hi > ep:
                    ep = hi
                    af = min(af + af_long, af_max_long)
                sar = sar + af * (ep - sar)
                if not first:
                    sar = min(sar, prev_low)
                sar = min(sar, lo)
        else:
            if hi >= sar:  # flip short -> long
                is_long = True
                sar = ep
                if offset_on_reverse != 0.0:
                    sar -= sar * offset_on_reverse
                sar = min(sar, prev_low, lo)
                out[row] = sar
                ep, af = hi, af_init_long
                sar = sar + af * (ep - sar)  # advance the new long leg one step
                sar = min(sar, prev_low, lo)
            else:
                out[row] = -sar
                if lo < ep:
                    ep = lo
                    af = min(af + af_short, af_max_short)
                sar = sar + af * (ep - sar)
                if not first:
                    sar = max(sar, prev_high)
                sar = max(sar, hi)
        prev_high, prev_low = hi, lo
    return pd.Series(out, index=df.index)


@INDICATORS.register
class SAREXT(Indicator):
    """Extended Parabolic SAR (SAREXT).

    What: a Parabolic SAR with independent long/short acceleration, an optional fixed seed and
        reversal offset, and a sign-encoded output (positive = long stop, negative = short stop).
    Best settings: TA-Lib defaults (0.02 / 0.02 / 0.2 per side); raise the init/step for a
        tighter, twitchier trailing stop.
    Edge cases: first bar NaN (seeded from the first two bars' directional movement); a single
        bar (or empty frame) is all NaN; on a flip the stop jumps to the prior extreme and is
        clamped out of the two most recent bars' range.
    Parity: ``talib.SAREXT`` (default params) on the finite overlap — exact seed/reversal step
        ordering (pandas-ta's pure-python port seeds differently).
    """

    spec = IndicatorSpec(
        name="sarext",
        category="trend",
        aliases=("Extended Parabolic SAR", "SAREXT", "Parabolic SAR Extended"),
        inputs=(HIGH, LOW),
        outputs=("sarext",),
        stateful=True,
        talib_compatible=True,
        references=("Wilder 1978", "TA-Lib SAREXT"),
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        start_value: float = Field(default=0.0)
        offset_on_reverse: float = Field(default=0.0, ge=0.0)
        af_init_long: float = Field(default=0.02, gt=0.0, le=1.0)
        af_long: float = Field(default=0.02, gt=0.0, le=1.0)
        af_max_long: float = Field(default=0.2, gt=0.0, le=1.0)
        af_init_short: float = Field(default=0.02, gt=0.0, le=1.0)
        af_short: float = Field(default=0.02, gt=0.0, le=1.0)
        af_max_short: float = Field(default=0.2, gt=0.0, le=1.0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        p = self.params
        return sarext(
            df,
            p["start_value"],
            p["offset_on_reverse"],
            p["af_init_long"],
            p["af_long"],
            p["af_max_long"],
            p["af_init_short"],
            p["af_short"],
            p["af_max_short"],
        )
