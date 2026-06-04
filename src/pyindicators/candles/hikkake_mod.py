"""CDLHIKKAKEMOD — Modified Hikkake Pattern (multi-bar, stateful, bidirectional).

A refinement of the Hikkake: a three-bar contracting "nest" whose middle bar also closes at
the extreme of its own range, followed by a breakout that confirms the trap. TA-Lib detects a
*setup* on bar ``i`` and then watches the next few bars for a *confirmation*; the two events
emit different magnitudes, so this pattern's outputs are ``-200/-100/0/100/200`` (NOT the usual
``-100/0/100`` — both the setup bar and its confirmation can fire, and a confirmation adds a
second ``±100``).

TA-Lib's ``TA_CDLHIKKAKEMOD`` (verified bit-exact against ``talib`` on synthetic + real bars):

Setup (the "nest"), evaluated on bar ``i`` using bars ``i-3 .. i``::

    high[i-2] < high[i-3] AND low[i-2] > low[i-3]      # i-2 sits inside i-3
    AND high[i-1] < high[i-2] AND low[i-1] > low[i-2]  # i-1 sits inside i-2
    AND (
        # bullish setup (+100): i breaks DOWN out of the nest, and i-2 closed near its low
        ( high[i] < high[i-1] AND low[i] < low[i-1]
          AND close[i-2] <= low[i-2]  + Near_avg(i-2) )
        OR
        # bearish setup (-100): i breaks UP out of the nest, and i-2 closed near its high
        ( high[i] > high[i-1] AND low[i] > low[i-1]
          AND close[i-2] >= high[i-2] - Near_avg(i-2) )
    )

On a setup TA-Lib emits ``patternResult`` (``+100`` if ``high[i] < high[i-1]`` else ``-100``)
and remembers ``(patternResult, patternIdx=i)``.

Confirmation, evaluated on a later bar ``i`` only when no new setup fires there::

    i <= patternIdx + 3
    AND ( ( patternResult > 0 AND close[i] > high[patternIdx-1] )
          OR ( patternResult < 0 AND close[i] < low[patternIdx-1] ) )

On a confirmation TA-Lib emits ``patternResult + 100 * sign(patternResult)`` — i.e. ``±200`` —
and clears the remembered setup (``patternIdx = 0``). Anything else emits ``0``.

The only sized comparison is the ``Near`` setting ``(HighLow, 5, 0.2)`` taken on bar ``i-2``;
its 5-bar average ends at bar ``i-3``, so TA-Lib's lookback is ``avgPeriod(Near) + 5 == 10``
(the first 10 bars are 0). The pattern is genuinely stateful — a setup and its confirmation
span up to four bars and carry across the array — so it is computed with a single forward pass.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_average

# TA-Lib lookback for CDLHIKKAKEMOD is max(1, avgPeriod(Near)) + 5 == 5 + 5 == 10.
_LOOKBACK = 10


def hikkake_mod(df: pd.DataFrame) -> pd.Series:
    """Modified Hikkake pattern over ``df`` (OHLC) as a -200/-100/0/100/200 ``Series``.

    Matches ``talib.CDLHIKKAKEMOD`` bit-exactly: ``±100`` on a setup ("nest" breakout with the
    middle bar closing at its extreme), ``±200`` on the breakout that confirms it within three
    bars, ``0`` elsewhere. The first 10 bars are 0 (TA-Lib lookback).
    """
    high = df[HIGH].to_numpy(dtype="float64")
    low = df[LOW].to_numpy(dtype="float64")
    close = df[CLOSE].to_numpy(dtype="float64")
    # ``Near`` average per bar (NaN during its 5-bar warm-up -> setup cannot fire there).
    near = candle_average(df, "Near").to_numpy()
    n = len(close)
    out = np.zeros(n, dtype="float64")

    # Stateful single forward pass. State carries across bars; a setup is remembered until it is
    # confirmed or expires. Bars before ``_LOOKBACK`` build state but emit 0 (TA-Lib lookback).
    pattern_idx = 0
    pattern_result = 0
    for i in range(3, n):
        nest = (
            high[i - 2] < high[i - 3]
            and low[i - 2] > low[i - 3]
            and high[i - 1] < high[i - 2]
            and low[i - 1] > low[i - 2]
        )
        near_i2 = near[i - 2]
        bullish = (
            nest
            and high[i] < high[i - 1]
            and low[i] < low[i - 1]
            and not np.isnan(near_i2)
            and close[i - 2] <= low[i - 2] + near_i2
        )
        bearish = (
            nest
            and high[i] > high[i - 1]
            and low[i] > low[i - 1]
            and not np.isnan(near_i2)
            and close[i - 2] >= high[i - 2] - near_i2
        )

        if bullish or bearish:
            pattern_result = 100 if high[i] < high[i - 1] else -100
            pattern_idx = i
            emitted = pattern_result
        elif i <= pattern_idx + 3 and (
            (pattern_result > 0 and close[i] > high[pattern_idx - 1])
            or (pattern_result < 0 and close[i] < low[pattern_idx - 1])
        ):
            emitted = pattern_result + (100 if pattern_result > 0 else -100)
            pattern_idx = 0
        else:
            emitted = 0

        if i >= _LOOKBACK:
            out[i] = emitted

    return pd.Series(out, index=df.index)


@INDICATORS.register
class HikkakeMod(Indicator):
    """Modified Hikkake candlestick pattern.

    What: a three-bar contracting nest (each bar inside the prior) whose middle bar closes at
    its extreme, then a breakout that confirms the trap within three bars.
    Best settings: parameterless; bullish setup breaks down, bearish setup breaks up.
    Edge cases: emits ``±200`` on a confirmed breakout (setup ``±100`` plus a second ``±100``),
    so outputs span ``{-200, -100, 0, 100, 200}``; first 10 bars are 0 (TA-Lib lookback).
    Parity: TA-Lib ``CDLHIKKAKEMOD`` (Near = HighLow/5/0.2 on bar i-2), exact integer match.
    """

    class Params(BaseModel):
        """CDLHIKKAKEMOD takes no parameters (TA-Lib exposes none)."""

        model_config = ConfigDict(extra="forbid", frozen=True)

    spec = IndicatorSpec(
        name="hikkake_mod",
        category="candles",
        aliases=("HikkakeMod", "CDLHIKKAKEMOD"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("hikkake_mod",),
        # ±200 is reachable: a confirmed breakout adds a second ±100 to the setup (see module
        # docstring), and ``talib.CDLHIKKAKEMOD`` emits it, so bounds span the true output range.
        bounds={"hikkake_mod": (-200.0, 200.0)},
        talib_compatible=True,
        references=("TA-Lib CDLHIKKAKEMOD",),
        doc="ref/ta_docs/candles/candlestick_patterns.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return hikkake_mod(df)
