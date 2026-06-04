"""VWMA — Volume Weighted Moving Average: ``sum(close*volume, N) / sum(volume, N)``."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, VOLUME, Indicator, IndicatorSpec, safe_divide


def vwma(df: pd.DataFrame, length: int = 20) -> pd.Series:
    """Volume Weighted Moving Average over ``length`` bars."""
    pv = (df[CLOSE] * df[VOLUME]).rolling(length, min_periods=length).sum()
    vol = df[VOLUME].rolling(length, min_periods=length).sum()
    return safe_divide(pv, vol)


@INDICATORS.register
class VWMA(Indicator):
    """Volume Weighted Moving Average.

    What: a moving average weighting each close by its volume.
    Best settings: ``length`` 20.
    Edge cases: sum(volume) == 0 over the window -> guarded to NaN.
    Parity: pandas-ta ``vwma`` / finta ``VW_MA``.
    """

    spec = IndicatorSpec(
        name="vwma",
        category="trend",
        aliases=("Volume Weighted MA",),
        inputs=(CLOSE, VOLUME),
        outputs=("vwma",),
        references=("pandas-ta vwma",),
        doc="ref/ta_docs/trend/misc_MA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return vwma(df, self.params["length"])
