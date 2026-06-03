"""Supertrend — ATR trailing-stop / trend-direction line (Olivier Seban ~2009).

Bands a multiple of ATR around hl2, with a carry-forward rule so the active band only
tightens until price closes through it, flipping the trend. Stateful (path-dependent).
Composes ``volatility.atr``. See ``ref/ta_docs/trend/Supertrend.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec

from .atr import atr


def supertrend(df: pd.DataFrame, length: int = 10, mult: float = 3.0) -> dict:
    """Supertrend line and direction (+1 uptrend / -1 downtrend)."""
    a = atr(df, length).to_numpy()
    hl2 = ((df[HIGH] + df[LOW]) / 2.0).to_numpy()
    close = df[CLOSE].to_numpy()
    n = close.size
    basic_upper = hl2 + mult * a
    basic_lower = hl2 - mult * a
    fu = np.full(n, np.nan)
    fl = np.full(n, np.nan)
    line = np.full(n, np.nan)
    direction = np.full(n, np.nan)

    valid = np.flatnonzero(~np.isnan(a))
    if valid.size:
        s = int(valid[0])  # first bar with a defined ATR
        fu[s], fl[s] = basic_upper[s], basic_lower[s]
        direction[s], line[s] = 1.0, basic_lower[s]  # seed assuming uptrend; self-corrects
        for i in range(s + 1, n):
            fu[i] = basic_upper[i] if (basic_upper[i] < fu[i - 1] or close[i - 1] > fu[i - 1]) else fu[i - 1]
            fl[i] = basic_lower[i] if (basic_lower[i] > fl[i - 1] or close[i - 1] < fl[i - 1]) else fl[i - 1]
            if direction[i - 1] == 1.0:  # was uptrend (line tracks lower band)
                direction[i], line[i] = (-1.0, fu[i]) if close[i] < fl[i] else (1.0, fl[i])
            else:  # was downtrend (line tracks upper band)
                direction[i], line[i] = (1.0, fl[i]) if close[i] > fu[i] else (-1.0, fu[i])

    return {
        "supertrend": pd.Series(line, index=df.index),
        "supertrend_dir": pd.Series(direction, index=df.index),
    }


@INDICATORS.register
class Supertrend(Indicator):
    """Supertrend.

    What: an ATR trailing-stop line plus trend direction (+1 long / -1 short).
    Best settings: ATR 10, mult 3 (general); 7/2 scalping, 14/4 swing.
    Edge cases: needs ATR warm-up; path-dependent carry-forward (stateful).
    Parity: pandas-ta ``supertrend`` family (variant/seed dependent — validated structurally).
    """

    spec = IndicatorSpec(
        name="supertrend",
        category="trend",
        aliases=("Supertrend",),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("supertrend", "supertrend_dir"),
        stateful=True,
        references=("Seban", "pandas-ta supertrend"),
        doc="ref/ta_docs/trend/Supertrend.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=10, ge=1)
        mult: float = Field(default=3.0, gt=0)

    def _compute(self, df: pd.DataFrame) -> dict:
        return supertrend(df, self.params["length"], self.params["mult"])
