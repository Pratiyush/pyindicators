"""Big Shadow — wide-range engulfing bar (two-bar, directional, magnitude 100).

The "Big Shadow" (Connors & Raschke, *Street Smarts*; also discussed by Nison) is a
**wide-range bar whose high-low range engulfs the prior bar's range**. It is the
*range*-based cousin of the body-based :mod:`engulfing` pattern: instead of body-engulfs-body,
the whole bar (high to low) swallows the previous bar AND is unusually large versus recent
bars. Such a bar marks a decisive, high-conviction session and is read directionally::

    range-engulf : high > prev_high  AND  low < prev_low      # this bar's range covers the prior bar
    wide         : (high - low)      >  factor * avg_range     # much larger than the recent average range
    bullish (+100): the wide engulfing bar closes up   (close >= open, a white candle)
    bearish (-100): the wide engulfing bar closes down (close <  open, a black candle)

where ``avg_range`` is the mean high-low range over the ``avg_period`` bars **ending at the
previous bar** (i.e. ``shift(1).rolling(avg_period)`` — the current bar is *excluded*). Using a
trailing, current-bar-exclusive window is what makes the signal **causal** (bar ``i`` depends
only on rows ``<= i``) and mirrors TA-Lib's ``CandleSetting`` averaging convention in
:func:`pyindicators.candles._candles.candle_average`. The first ``avg_period`` bars cannot
have a full window, so their average is ``NaN``; the comparison ``range > factor*NaN`` is then
``False`` and those warm-up bars correctly emit ``0`` (no fabricated signals).

Output is **+100 / 0 / -100** (direction, not magnitude — there is no partial ±80 score; the
"wide" test is a strict inequality against an average, so a bar never merely "ties").

GOLDEN-ONLY: no reference library (TA-Lib, pandas-ta, finta, ``ta``) implements "Big Shadow",
so there is no oracle to match. The definition above is the closed form; correctness is pinned
by structural/closed-form assertions in ``tests/candles/test_big_shadow.py`` and
``tests/parity/test_parity_big_shadow.py`` (constructed bars with known outcomes + the
range-engulf/wide invariants checked directly on ``deterministic_frame()``).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec

from ._candles import candle_color, hl_range


def big_shadow(df: pd.DataFrame, avg_period: int = 10, factor: float = 2.0) -> pd.Series:
    """Big Shadow (wide-range engulfing bar) over ``df`` (OHLC) as a -100/0/100 ``Series``.

    A bar is a Big Shadow when its high-low range engulfs the prior bar's range
    (``high > prev_high`` and ``low < prev_low``) **and** that range exceeds ``factor`` times
    the average range of the ``avg_period`` bars ending at the previous bar. The sign is the
    bar's colour (+100 white / -100 black). The first ``avg_period`` bars are ``0`` (the
    trailing average is undefined during warm-up, so no signal can fire).
    """
    rng = hl_range(df)
    prev_high = df[HIGH].shift(1)
    prev_low = df[LOW].shift(1)
    # Average range over the avg_period bars ending at i-1 (current bar excluded -> causal),
    # matching TA-Lib's CandleSetting averaging; NaN until the window first fills.
    avg_range = rng.shift(1).rolling(window=avg_period, min_periods=avg_period).mean()

    range_engulf = (df[HIGH] > prev_high) & (df[LOW] < prev_low)
    wide = rng > factor * avg_range  # NaN avg during warm-up -> False -> no signal
    hit = (range_engulf & wide).to_numpy()

    color = candle_color(df).to_numpy()  # +1 white (close >= open) / -1 black
    out = np.where(hit, color * 100.0, 0.0)
    out[:avg_period] = 0.0  # warm-up lookback: first avg_period bars are always 0
    return pd.Series(out, index=df.index)


@INDICATORS.register
class BigShadow(Indicator):
    """Big Shadow (wide-range engulfing bar).

    What: a bar whose high-low range engulfs the prior bar AND is much larger than the recent
    average range — a decisive, high-conviction session; read by the bar's direction.
    Best settings: ``avg_period=10`` (trailing average range), ``factor=2.0`` ("much larger");
    raise ``factor`` for a stricter, rarer signal.
    Edge cases: first ``avg_period`` bars are 0 (warm-up); +100 white / -100 black; no partial
    score (the wide test is a strict inequality, so there is no ±80 tie case).
    Parity: GOLDEN-ONLY — no reference library implements Big Shadow; pinned by closed-form /
    structural tests (range-engulf + wide-range invariants), not an external oracle.
    """

    spec = IndicatorSpec(
        name="big_shadow",
        category="candles",
        aliases=("Big Shadow", "Wide Range Engulfing Bar", "WRB"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("big_shadow",),
        bounds={"big_shadow": (-100.0, 100.0)},
        talib_compatible=False,
        references=("Connors & Raschke, Street Smarts", "Nison candlesticks"),
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        avg_period: int = Field(default=10, ge=1)
        factor: float = Field(default=2.0, gt=0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return big_shadow(df, self.params["avg_period"], self.params["factor"])
