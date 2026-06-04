"""SINWMA — Sine Weighted Moving Average (weights = sine of position; symmetric)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from ._weighted import weighted_ma


def sinwma(close: pd.Series, length: int = 14) -> pd.Series:
    """Sine Weighted MA (weights ``sin(pi*i/(N+1))``, i=1..N; emphasises the window centre)."""
    i = np.arange(1, length + 1)
    weights = np.sin(np.pi * i / (length + 1))
    return weighted_ma(close, weights)


@INDICATORS.register
class SINWMA(Indicator):
    """Sine Weighted Moving Average.

    What: a weighted MA with sine-shaped weights that emphasise the middle of the window.
    Best settings: ``length`` 14.
    Edge cases: first ``length-1`` bars NaN.
    Parity: pandas-ta ``sinwma``.
    """

    spec = IndicatorSpec(
        name="sinwma",
        category="trend",
        aliases=("Sine Weighted MA",),
        inputs=(CLOSE,),
        outputs=("sinwma",),
        references=("pandas-ta sinwma",),
        doc="ref/ta_docs/trend/misc_MA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return sinwma(df[CLOSE], self.params["length"])
