"""CKSP — Chande Kroll Stop (trend-following ATR stops; Chande & Kroll).

Two trailing stop levels derived from recent extremes minus/plus an ATR band, then
smoothed by a rolling extreme over ``q`` bars. ``Long stop = max_q( HH(p) - x*ATR(p) )`` and
``Short stop = min_q( LL(p) + x*ATR(p) )``. This is the TradingView mode (Wilder/RMA ATR,
defaults p=10, x=1, q=9); the book mode (SMA ATR, 10/3/20) is reachable via params.
Composes ``volatility.atr``. See ``ref/ta_docs/trend/CKSP.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma, true_range
from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec
from pyindicators.volatility.atr import atr


def cksp(
    df: pd.DataFrame,
    p: int = 10,
    x: float = 1.0,
    q: int = 9,
    tvmode: bool = True,
) -> dict:
    """Chande Kroll Stop long/short trailing-stop levels.

    ``tvmode`` (default) uses Wilder/RMA-smoothed ATR; ``tvmode=False`` uses SMA-smoothed
    ATR (the original "New Technical Trader" book variant). The ATR mode is the only
    behavioural difference — the rolling-extreme construction is identical to ``cksp`` in
    pandas-ta-classic, whose narrative docstring mislabels the short leg as ``high.min()``
    while its code (matched here) correctly uses ``low.min()``.
    """
    atr_ = atr(df, p) if tvmode else sma(true_range(df), p)

    long_stop_ = df[HIGH].rolling(p, min_periods=p).max() - x * atr_
    long_stop = long_stop_.rolling(q, min_periods=q).max()

    short_stop_ = df[LOW].rolling(p, min_periods=p).min() + x * atr_
    short_stop = short_stop_.rolling(q, min_periods=q).min()

    return {"cksp_long": long_stop, "cksp_short": short_stop}


@INDICATORS.register
class CKSP(Indicator):
    """Chande Kroll Stop.

    What: ATR-banded trailing stops smoothed by a rolling extreme — a long stop below price
    (from recent highs) and a short stop above price (from recent lows).
    Best settings: TV mode p=10, x=1, q=9; book mode p=10, x=3, q=20 (set ``tvmode=False``).
    Edge cases: inherits ATR warm-up; first value at index ``p+q-2``; flat market -> ATR 0
    so stops sit exactly on HH/LL.
    Parity: pandas-ta-classic ``cksp`` (TV mode, RMA ATR). Wilder seeding -> tail/rtol.
    """

    spec = IndicatorSpec(
        name="cksp",
        category="trend",
        aliases=("Chande Kroll Stop", "CKSP"),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("cksp_long", "cksp_short"),
        references=("Chande & Kroll, The New Technical Trader", "pandas-ta cksp"),
        doc="ref/ta_docs/trend/CKSP.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        p: int = Field(default=10, ge=1)
        x: float = Field(default=1.0, gt=0)
        q: int = Field(default=9, ge=1)
        tvmode: bool = Field(default=True)

    def _compute(self, df: pd.DataFrame) -> dict:
        prm = self.params
        return cksp(df, prm["p"], prm["x"], prm["q"], prm["tvmode"])
