"""Spring — Wyckoff Spring / Upthrust false-breakout bar (structural, magnitude ±100).

A Wyckoff **Spring** is a *false breakdown*: a bar that probes **below** a recent support
level intrabar but **closes back above** it, trapping breakout sellers — a bullish shakeout.
Its mirror image, the **Upthrust** (a.k.a. "upthrust after distribution"), is a *false
breakout*: a bar that probes **above** a recent resistance level but closes back below it — a
bearish trap. This indicator emits ``+100`` on a spring, ``-100`` on an upthrust, ``0``
otherwise.

There is **no TA-Lib / pandas-ta oracle** for this pattern, so it is pinned to an explicit,
documented closed-form rule (golden-tested; the parity file carries the structural assertions
rather than a reference-library comparison).

The rule at bar ``i`` with window ``length = N`` (support/resistance are the **prior** ``N``
bars, EXCLUSIVE of the current bar, so the signal is strictly causal — no look-ahead)::

    support(i)    = min(low [i-N .. i-1])          # rolling low  of the N bars before i
    resistance(i) = max(high[i-N .. i-1])          # rolling high of the N bars before i

    spring  (+100): low (i) <  support(i)    AND close(i) >  support(i)
    upthrust(-100): high(i) >  resistance(i) AND close(i) <  resistance(i)
    else     0

All four comparisons are **strict** (``<`` / ``>``): merely *touching* support/resistance, or
closing exactly on it, is not a reversal — the bar must genuinely pierce the level and reclaim
it. A flat/constant series therefore never fires (``x < x`` is ``False``). During the warm-up
(the first ``N`` bars the rolling window is not yet full) the thresholds are ``NaN`` so every
comparison is ``False``; those bars are emitted as ``0`` (not ``NaN``) so the column is finite
after warm-up and the result is truncation-invariant. A spring and an upthrust cannot both fire
on the same bar (a single close cannot be simultaneously above the prior-low support and below
the prior-high resistance, since support <= resistance), so the output is always exactly one of
``{-100, 0, 100}``.
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec


def spring(df: pd.DataFrame, length: int = 20) -> pd.Series:
    """Wyckoff Spring / Upthrust over ``df`` (OHLC) as a -100/0/100 ``Series``.

    ``+100`` where the bar's low pierces the prior ``length``-bar support (rolling low) yet the
    close reclaims it (a bullish spring); ``-100`` where the high pierces the prior
    ``length``-bar resistance (rolling high) yet the close falls back below it (a bearish
    upthrust); ``0`` otherwise. The first ``length`` bars are ``0`` (warm-up). See the module
    docstring for the exact closed-form rule.
    """
    high = df[HIGH].to_numpy(dtype="float64")
    low = df[LOW].to_numpy(dtype="float64")
    close = df[CLOSE].to_numpy(dtype="float64")

    # Trailing support/resistance over the N bars ENDING AT i-1 (current bar excluded): a closed
    # rolling extreme that requires a full window, shifted out by one bar. NaN until the window
    # fills -> every comparison below is False during the warm-up.
    low_s = df[LOW]
    high_s = df[HIGH]
    support = low_s.rolling(window=length, min_periods=length).min().shift(1).to_numpy()
    resistance = high_s.rolling(window=length, min_periods=length).max().shift(1).to_numpy()

    spring_hit = (low < support) & (close > support)  # false breakdown, reclaimed -> bullish
    upthrust_hit = (high > resistance) & (close < resistance)  # false breakout, rejected -> bearish

    out = np.where(spring_hit, 100.0, np.where(upthrust_hit, -100.0, 0.0))
    out[:length] = 0.0  # warm-up: thresholds undefined for the first ``length`` bars
    return pd.Series(out, index=df.index)


@INDICATORS.register
class Spring(Indicator):
    """Wyckoff Spring / Upthrust false-breakout pattern.

    What: a bar that probes beyond recent support/resistance intrabar but closes back inside it
    — a trapped-breakout reversal. ``+100`` = bullish spring (false breakdown of the prior-``N``
    rolling low, reclaimed at the close); ``-100`` = bearish upthrust (false breakout of the
    prior-``N`` rolling high, rejected at the close); ``0`` otherwise.
    Best settings: ``length`` 20 (a month of daily support/resistance); shorten for faster
    timeframes. All four piercing/reclaim comparisons are strict.
    Edge cases: first ``length`` bars are 0 (warm-up); a flat/constant series never fires;
    spring and upthrust are mutually exclusive, so the output is exactly one of {-100, 0, 100}.
    Parity: no TA-Lib/pandas-ta oracle — pinned to the documented closed-form rule (golden +
    structural tests).
    """

    class Params(BaseModel):
        """Parameters for Spring (the lookback for the support/resistance window)."""

        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=1)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="spring",
        category="candles",
        aliases=("Spring", "Wyckoff Spring", "Upthrust"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("spring",),
        bounds={"spring": (-100.0, 100.0)},
        talib_compatible=False,
        references=("Wyckoff method (Spring / Upthrust)",),
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return spring(df[list(self.spec.inputs)], self.params["length"])
