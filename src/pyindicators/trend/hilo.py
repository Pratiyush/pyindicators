"""Gann HiLo Activator (HILO) — SMA-band trend-follower (Robert Krausz, 1998).

Two simple moving averages — one of the highs, one of the lows — form an upper and a lower
band. A single stateful line flips between them: it jumps to the low-band when ``close``
crosses *above* the prior high-band, and to the high-band when ``close`` crosses *below* the
prior low-band; otherwise it carries forward. Path-dependent (stateful). Composes
``base.sma``. See ``ref/ta_docs/trend/HILO.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def hilo(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    high_length: int = 13,
    low_length: int = 21,
) -> dict:
    """Gann HiLo Activator line plus its long/short legs.

    ``hilo`` is the active band. ``hilo_long`` carries the value on bars where the line jumps
    to (or, while in an uptrend, holds at) the low-band; ``hilo_short`` mirrors that for the
    high-band. On a *flip* bar exactly one leg is set; on a *carry-forward* bar both legs take
    the held value (matching pandas-ta), so ``hilo_long.fillna(hilo_short) == hilo`` wherever
    defined. The flip uses the *prior* bar's bands (``i-1``), so the result is causal. Bars
    before the longer SMA warms up — and any bar before the first cross — are NaN.
    """
    high_ma = sma(high, high_length).to_numpy()
    low_ma = sma(low, low_length).to_numpy()
    c = close.to_numpy()
    n = c.size

    line = np.full(n, np.nan)
    long_leg = np.full(n, np.nan)
    short_leg = np.full(n, np.nan)

    for i in range(1, n):
        # NaN comparisons are False, so before both bands warm up neither branch fires and
        # the line stays NaN — matching pandas-ta's stateful loop exactly.
        if c[i] > high_ma[i - 1]:
            line[i] = long_leg[i] = low_ma[i]
        elif c[i] < low_ma[i - 1]:
            line[i] = short_leg[i] = high_ma[i]
        else:
            line[i] = line[i - 1]
            long_leg[i] = short_leg[i] = line[i - 1]

    return {
        "hilo": pd.Series(line, index=close.index),
        "hilo_long": pd.Series(long_leg, index=close.index),
        "hilo_short": pd.Series(short_leg, index=close.index),
    }


@INDICATORS.register
class HiLo(Indicator):
    """Gann HiLo Activator.

    What: an SMA(high)/SMA(low) channel with a stateful line that flips to the opposite band
    as ``close`` crosses the prior band — a trend/trailing-stop overlay.
    Best settings: 13/21 (Krausz); raise ``high_length`` / lower ``low_length`` for shorts,
    the reverse for longs.
    Edge cases: needs ``max(high_length, low_length)`` warm-up; carry-forward is
    path-dependent (stateful); a flat series never crosses (strict ``<``/``>``) so stays NaN.
    Parity: pandas-ta(_classic) ``hilo`` (SMA mamode), exact.
    """

    spec = IndicatorSpec(
        name="hilo",
        category="trend",
        aliases=("Gann HiLo Activator", "Gann High Low", "HILO"),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("hilo", "hilo_long", "hilo_short"),
        stateful=True,
        references=("Krausz 1998", "pandas-ta hilo"),
        doc="ref/ta_docs/trend/HILO.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        high_length: int = Field(default=13, ge=1)
        low_length: int = Field(default=21, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        return hilo(
            df[HIGH],
            df[LOW],
            df[CLOSE],
            self.params["high_length"],
            self.params["low_length"],
        )
