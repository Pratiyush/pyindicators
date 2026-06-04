"""RSL — Relative Strength Levy (Robert A. Levy's relative-strength ratio).

Price relative to its own simple moving average: ``close / SMA(close, length)`` (Levy 1967,
default length 26). A pure ratio centred on ~1.0 — above 1 means price leads its average
(relative strength), below 1 means it lags. This is Levy's RSL, NOT Wilder's bounded RSI.
Composes ``base.sma`` and guards the division with ``core.safe_divide``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide


def rsl(close: pd.Series, length: int = 26) -> pd.Series:
    """Levy's Relative Strength: ``close / SMA(close, length)`` (ratio, ~1.0 baseline).

    First ``length-1`` bars are NaN (SMA warm-up). A zero SMA basis (only reachable with a
    flat window at price 0) is guarded to NaN rather than fabricating +/-inf.
    """
    return safe_divide(close, sma(close, length))


@INDICATORS.register
class RSL(Indicator):
    """Relative Strength Levy.

    What: price divided by its own SMA — an unbounded relative-strength ratio around 1.0.
    Best settings: 26 (Levy's classic monthly/weekly setting); compare across symbols to rank.
    Edge cases: warm-up is NaN; flat window at price 0 -> 0/0 -> NaN (guarded, not inf).
    Parity: closed-form ``close / SMA`` — cross-checked against pandas-ta ``sma`` (exact).
    """

    spec = IndicatorSpec(
        name="rsl",
        category="momentum",
        aliases=("Relative Strength Levy", "Levy Relative Strength"),
        inputs=(CLOSE,),
        outputs=("rsl",),
        talib_compatible=False,
        references=("Levy 1967", "close / SMA(close, length)"),
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=26, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return rsl(df[CLOSE], self.params["length"])
