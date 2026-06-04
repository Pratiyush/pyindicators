"""TTM Momentum (John Carter) — the squeeze histogram.

Linear-regression value of ``close - ((Donchian-mid + SMA) / 2)`` over ``length`` bars: the
momentum component plotted with the TTM Squeeze. Composes ``base.sma`` + ``statistics.linreg``.
See ``ref/ta_docs/momentum/misc_momentum.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec
from pyindicators.statistics.linreg import linreg


def ttm_momentum(df: pd.DataFrame, length: int = 20) -> pd.Series:
    """TTM squeeze momentum histogram (linreg of close minus the Donchian/SMA midline)."""
    hh = df[HIGH].rolling(length, min_periods=length).max()
    ll = df[LOW].rolling(length, min_periods=length).min()
    midline = ((hh + ll) / 2.0 + sma(df[CLOSE], length)) / 2.0
    return linreg(df[CLOSE] - midline, length)


@INDICATORS.register
class TTMMomentum(Indicator):
    """TTM Momentum.

    What: the squeeze histogram — momentum direction/strength shown with the TTM Squeeze.
    Best settings: ``length`` 20; rising above zero = bullish momentum.
    Edge cases: warm-up = length (Donchian) + length (linreg); needs >= 2 for the regression.
    Parity: pandas-ta ``squeeze`` momentum column.
    """

    spec = IndicatorSpec(
        name="ttm_momentum",
        category="momentum",
        aliases=("TTM Squeeze Momentum",),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("ttm_momentum",),
        references=("Carter", "pandas-ta squeeze"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=2)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return ttm_momentum(df, self.params["length"])
