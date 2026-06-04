"""QQE — Quantitative Qualitative Estimation (EarnForex/Hyder/Ignatov).

A smoothed-RSI trend system, structurally like SuperTrend but on RSI instead of price:
take an EMA-smoothed RSI, build a Wilder-ATR-style volatility band around it from the
double-EMA-smoothed absolute one-bar change of that smoothed RSI (times a ``factor``, 4.236
by default), then trail a long line below and a short line above. ``qqe`` is the active
trailing line, flipping long/short as the smoothed RSI crosses the opposite band; ``qqe_long``
and ``qqe_short`` are the sparse per-trend signal lines.

Composes ``momentum.rsi`` and ``base.ema``. The smoothing chain is RSI -> EMA(RSI, smooth)
-> EMA(|d EMA-RSI|, 2*length-1) -> EMA(., 2*length-1) (Wilder's length expressed as an EMA).
See ``ref/ta_docs/momentum/misc_momentum.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from .rsi import rsi


def _qqe_trail(rsi_ma: np.ndarray, ub: np.ndarray, lb: np.ndarray) -> dict[str, np.ndarray]:
    """Trail the long/short lines and pick the active QQE line (SuperTrend-on-RSI recurrence).

    ``qqe`` is the active trailing line; ``qqe_long`` / ``qqe_short`` carry the line only on
    bars whose trend is long / short respectively (NaN otherwise), matching pandas-ta's sparse
    ``QQEl`` / ``QQEs`` signal columns. The recurrence is stateful (each bar depends on the
    previous two), so it is computed iteratively over the warmed band arrays.
    """
    m = rsi_ma.size
    long_line = np.zeros(m)
    short_line = np.zeros(m)
    trend = np.ones(m)
    qqe = np.empty(m)
    qqe[0] = rsi_ma[0]
    qqe_long = np.full(m, np.nan)
    qqe_short = np.full(m, np.nan)
    for i in range(1, m):
        c_rsi, p_rsi = rsi_ma[i], rsi_ma[i - 1]
        c_long, c_short = long_line[i - 1], short_line[i - 1]
        p_long = long_line[i - 2] if i >= 2 else 0.0
        p_short = short_line[i - 2] if i >= 2 else 0.0
        # Long line ratchets up while RSI stays above it, else snaps to the lower band.
        long_line[i] = max(c_long, lb[i]) if (p_rsi > c_long and c_rsi > c_long) else lb[i]
        # Short line ratchets down while RSI stays below it, else snaps to the upper band.
        short_line[i] = min(c_short, ub[i]) if (p_rsi < c_short and c_rsi < c_short) else ub[i]
        # Trend flips when RSI crosses the opposite line; otherwise carry the prior trend.
        if (c_rsi > c_short and p_rsi < p_short) or (c_rsi <= c_short and p_rsi >= p_short):
            trend[i] = 1.0
            qqe[i] = qqe_long[i] = long_line[i]
        elif (c_rsi > c_long and p_rsi < p_long) or (c_rsi <= c_long and p_rsi >= p_long):
            trend[i] = -1.0
            qqe[i] = qqe_short[i] = short_line[i]
        else:
            trend[i] = trend[i - 1]
            if trend[i] == 1.0:
                qqe[i] = qqe_long[i] = long_line[i]
            else:
                qqe[i] = qqe_short[i] = short_line[i]
    return {"qqe": qqe, "qqe_long": qqe_long, "qqe_short": qqe_short}


def qqe(
    close: pd.Series,
    length: int = 14,
    smooth: int = 5,
    factor: float = 4.236,
) -> dict[str, pd.Series]:
    """Quantitative Qualitative Estimation: active line, smoothed RSI, sparse long/short lines."""
    wilders_length = 2 * length - 1
    rsi_ma = ema(rsi(close, length), smooth)  # EMA-smoothed RSI (SMA-seeded, like pandas-ta)
    rsi_ma_tr = rsi_ma.diff().abs()  # one-bar "true range" of the smoothed RSI
    # Double EMA-smooth that range over Wilder's length, then scale -> band half-width.
    dar = factor * ema(ema(rsi_ma_tr, wilders_length), wilders_length)
    upperband = rsi_ma + dar
    lowerband = rsi_ma - dar
    idx = close.index
    trail = _qqe_trail(rsi_ma.to_numpy(), upperband.to_numpy(), lowerband.to_numpy())
    return {
        "qqe": pd.Series(trail["qqe"], index=idx),
        "qqe_rsima": rsi_ma,
        "qqe_long": pd.Series(trail["qqe_long"], index=idx),
        "qqe_short": pd.Series(trail["qqe_short"], index=idx),
    }


@INDICATORS.register
class QQE(Indicator):
    """Quantitative Qualitative Estimation (QQE).

    What: a SuperTrend-style trailing system built on an EMA-smoothed RSI with a
        Wilder-ATR-of-RSI band; ``qqe`` is the active line, ``qqe_rsima`` the smoothed RSI
        basis, and ``qqe_long`` / ``qqe_short`` the sparse per-trend signal lines.
    Best settings: length 14, smooth 5, factor 4.236 (EarnForex/TradingView defaults).
    Edge cases: long warm-up (smoothed RSI plus a double Wilder-length EMA of its range);
        the trailing recurrence is seeded from the first warmed band bar, so the active line's
        first bars depend on EMA seeding (pinned via a tail comparison in parity tests).
    Parity: pandas-ta ``qqe`` (QQE / QQE_RSIMA / QQEl / QQEs) on the warmed tail; seeding of
        the inner Wilder/EMA chain converges to machine precision well before the tail.
    """

    spec = IndicatorSpec(
        name="qqe",
        category="momentum",
        aliases=("Quantitative Qualitative Estimation",),
        inputs=(CLOSE,),
        outputs=("qqe", "qqe_rsima", "qqe_long", "qqe_short"),
        bounds={"qqe_rsima": (0.0, 100.0)},
        stateful=True,
        references=("EarnForex QQE.mq5", "pandas-ta qqe", "TradingView QQE"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)
        smooth: int = Field(default=5, ge=1)
        factor: float = Field(default=4.236, gt=0.0)

    def _compute(self, df: pd.DataFrame) -> dict[str, pd.Series]:
        p = self.params
        return qqe(df[CLOSE], p["length"], p["smooth"], p["factor"])
