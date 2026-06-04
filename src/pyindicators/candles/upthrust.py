"""Upthrust — Wyckoff Upthrust false-breakout bar (structural, bearish-only, magnitude -100).

A Wyckoff **Upthrust** (a.k.a. "upthrust after distribution") is a *false breakout*: a bar that
probes **above** a recent resistance level intrabar but **closes back below** it, trapping the
breakout buyers — a bearish rejection. This indicator isolates that single bearish leg and emits
``-100`` on an upthrust, ``0`` otherwise (it is a bearish-only signal — there is no ``+100``
case; its bullish mirror, the false breakdown that closes back above support, is the *Spring*).

There is **no TA-Lib / pandas-ta / finta / ta oracle** for this pattern, so it is pinned to an
explicit, documented closed-form rule (golden-tested; the parity file carries the structural
re-derivation rather than a reference-library comparison). The rule is the bearish leg of the
sibling ``spring`` indicator, kept bit-identical so the two agree on every bar.

The rule at bar ``i`` with window ``length = N`` (resistance is the **prior** ``N`` bars,
EXCLUSIVE of the current bar, so the signal is strictly causal — no look-ahead)::

    resistance(i) = max(high[i-N .. i-1])             # rolling high of the N bars before i
    upthrust(-100): high(i) > resistance(i) AND close(i) < resistance(i)
    else      0

Both comparisons are **strict** (``>`` / ``<``): merely *touching* the resistance, or closing
exactly on it, is not a rejection — the bar must genuinely pierce the level *and* fail to hold
it. A flat/constant series therefore never fires (``x > x`` is ``False``). During the warm-up
(the first ``N`` bars, where the rolling window is not yet full) the threshold is ``NaN`` so
every comparison is ``False``; those bars are emitted as ``0`` (not ``NaN``) so the column is
finite after warm-up and the result is truncation-invariant. The output is therefore always
exactly one of ``{-100, 0}`` (the bounds advertise ``[-100, 100]`` to match the candle-pattern
convention, but ``+100`` is never produced).
"""

from __future__ import annotations

from typing import ClassVar

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec


def upthrust(df: pd.DataFrame, length: int = 20) -> pd.Series:
    """Wyckoff Upthrust over ``df`` (OHLC) as a -100/0 ``Series``.

    ``-100`` where the bar's high pierces the prior ``length``-bar resistance (rolling high) yet
    the close falls back below it (a bearish false breakout); ``0`` otherwise. The first
    ``length`` bars are ``0`` (warm-up). See the module docstring for the exact closed-form rule.
    """
    high = df[HIGH].to_numpy(dtype="float64")
    close = df[CLOSE].to_numpy(dtype="float64")

    # Trailing resistance over the N bars ENDING AT i-1 (current bar excluded): a closed rolling
    # max that requires a full window, shifted out by one bar. NaN until the window fills -> both
    # comparisons below are False during the warm-up.
    resistance = df[HIGH].rolling(window=length, min_periods=length).max().shift(1).to_numpy()

    upthrust_hit = (high > resistance) & (close < resistance)  # false breakout, rejected -> bearish

    out = np.where(upthrust_hit, -100.0, 0.0)
    out[:length] = 0.0  # warm-up: resistance undefined for the first ``length`` bars
    return pd.Series(out, index=df.index)


@INDICATORS.register
class Upthrust(Indicator):
    """Wyckoff Upthrust false-breakout pattern (bearish-only).

    What: a bar that probes above the recent ``length``-bar resistance intrabar but closes back
    below it — a trapped-breakout bearish rejection. ``-100`` on an upthrust, ``0`` otherwise.
    The bullish mirror (false breakdown reclaimed above support) is the ``spring`` indicator;
    this isolates only the bearish leg, so there is no ``+100`` case.
    Best settings: ``length`` 20 (about a month of daily resistance); shorten for faster
    timeframes. Both the pierce and the close-back-below comparisons are strict.
    Edge cases: first ``length`` bars are 0 (warm-up); a flat/constant series never fires; the
    output is exactly one of {-100, 0} (bearish-only; bounds are [-100, 100] by convention).
    Parity: no TA-Lib/pandas-ta oracle — pinned to the documented closed-form rule (the bearish
    leg of ``spring``); golden + structural tests.
    """

    class Params(BaseModel):
        """Parameters for Upthrust (the lookback for the resistance window)."""

        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=1)

    spec: ClassVar[IndicatorSpec] = IndicatorSpec(
        name="upthrust",
        category="candles",
        aliases=("Upthrust", "Wyckoff Upthrust", "Upthrust After Distribution"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("upthrust",),
        bounds={"upthrust": (-100.0, 100.0)},
        talib_compatible=False,
        references=("Wyckoff method (Upthrust after distribution)",),
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return upthrust(df[list(self.spec.inputs)], self.params["length"])
