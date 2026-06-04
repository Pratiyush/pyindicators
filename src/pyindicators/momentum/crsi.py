"""Connors RSI (CRSI) — Larry Connors' composite short-term momentum/mean-reversion oscillator.

The mean of three equally weighted, 0-100 components: a short Wilder RSI of price, a short
Wilder RSI of the *streak* (signed consecutive up/down-close count), and the percent-rank of
the 1-bar rate of change over a long lookback. Composes ``momentum.rsi`` and ``momentum.roc``.
See ``ref/ta_docs/momentum/misc_momentum.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from .roc import roc
from .rsi import rsi


def _streak(close: pd.Series) -> pd.Series:
    """Signed run length of consecutive up/down closes (0 on an unchanged close).

    +1, +2, +3 ... on each successive higher close; -1, -2 ... on each successive lower close;
    resets to 0 whenever ``close`` is flat. The first bar has no prior close, so it is 0.
    """
    diff = close.to_numpy(dtype="float64")
    n = diff.size
    out = np.zeros(n, dtype="float64")
    for i in range(1, n):
        prev_c, cur_c = diff[i - 1], diff[i]
        if np.isnan(prev_c) or np.isnan(cur_c):
            out[i] = 0.0
        elif cur_c > prev_c:
            out[i] = out[i - 1] + 1.0 if out[i - 1] > 0 else 1.0
        elif cur_c < prev_c:
            out[i] = out[i - 1] - 1.0 if out[i - 1] < 0 else -1.0
        else:
            out[i] = 0.0
    return pd.Series(out, index=close.index)


def _percent_rank(series: pd.Series, length: int) -> pd.Series:
    """Connors' percent-rank: % of the *prior* ``length`` values strictly below the current.

    Per the original definition, today's value is compared against the one-bar values from each
    of the previous ``length`` bars (the window excludes the current bar); the count of values
    ``< current`` is divided by ``length`` and scaled to 0-100. Warm-up (fewer than ``length``
    prior values, or a NaN current value) yields NaN.
    """
    x = series.to_numpy(dtype="float64")
    n = x.size
    out = np.full(n, np.nan)
    for i in range(length, n):
        cur = x[i]
        if np.isnan(cur):
            continue
        window = x[i - length : i]  # the prior ``length`` values, excluding the current bar
        if np.isnan(window).any():
            continue
        out[i] = 100.0 * np.count_nonzero(window < cur) / length
    return pd.Series(out, index=series.index)


def crsi(
    close: pd.Series,
    rsi_length: int = 3,
    streak_length: int = 2,
    rank_length: int = 100,
) -> pd.Series:
    """Connors RSI: mean of RSI(close), RSI(streak) and PercentRank(1-bar ROC), bounded [0, 100]."""
    price_rsi = rsi(close, rsi_length)
    streak_rsi = rsi(_streak(close), streak_length)
    rank = _percent_rank(roc(close, length=1), rank_length)
    return (price_rsi + streak_rsi + rank) / 3.0


@INDICATORS.register
class ConnorsRSI(Indicator):
    """Connors RSI (CRSI).

    What: a 0-100 composite of short price-RSI, short streak-RSI and the percent-rank of the
        1-bar ROC — Larry Connors' short-term overbought/oversold mean-reversion oscillator.
    Best settings: 3 / 2 / 100 (Connors); <10/<5 oversold, >90/>95 overbought.
    Edge cases: a flat price RSI window -> NaN propagates; the percent-rank dominates the long
        warm-up (no value until ``rank_length`` prior 1-bar ROCs exist).
    Parity: Connors' published definition validated component-by-component (RSI vs pandas-ta
        ``rsi``; streak/percent-rank/composite vs the closed form) — no single library oracle.
    """

    spec = IndicatorSpec(
        name="crsi",
        category="momentum",
        aliases=("Connors RSI", "CRSI"),
        inputs=(CLOSE,),
        outputs=("crsi",),
        bounds={"crsi": (0.0, 100.0)},
        references=(
            "Connors & Alvarez, An Introduction to ConnorsRSI",
            "TradingView CRSI",
        ),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        rsi_length: int = Field(default=3, ge=1)
        streak_length: int = Field(default=2, ge=1)
        rank_length: int = Field(default=100, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        p = self.params
        return crsi(df[CLOSE], p["rsi_length"], p["streak_length"], p["rank_length"])
