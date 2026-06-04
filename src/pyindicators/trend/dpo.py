"""DPO — Detrended Price Oscillator (causal form).

Removes the trend to expose cycles: ``DPO = close - SMA(close, N) shifted back by N/2+1``.
We use the causal (non-centered) form ``close - SMA(close, N).shift(N//2 + 1)`` so it never
looks ahead. Composes ``base.sma``. See ``ref/ta_docs/trend/README.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def dpo(close: pd.Series, length: int = 20) -> pd.Series:
    """Detrended Price Oscillator (causal): close minus the SMA from N/2+1 bars ago."""
    return close - sma(close, length).shift(length // 2 + 1)


@INDICATORS.register
class DPO(Indicator):
    """Detrended Price Oscillator.

    What: price minus a displaced SMA — strips the trend to highlight cycles.
    Best settings: ``length`` 20. We use the causal (non-centered) variant.
    Edge cases: warm-up = length + N/2+1.
    Parity: pandas-ta ``dpo`` with ``centered=False``.
    """

    spec = IndicatorSpec(
        name="dpo",
        category="trend",
        aliases=("Detrended Price Oscillator",),
        inputs=(CLOSE,),
        outputs=("dpo",),
        references=("pandas-ta dpo (centered=False)",),
        doc="ref/ta_docs/trend/README.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return dpo(df[CLOSE], self.params["length"])
