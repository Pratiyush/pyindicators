"""Ulcer Index (UI) — downside-risk volatility (Peter Martin).

Root-mean-square of percentage drawdowns from the rolling high:
``dd = 100*(close - HH(N))/HH(N)``; ``UI = sqrt(mean(dd^2, N))``. Only penalises declines.
See ``ref/ta_docs/volatility/misc_volatility.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def ulcer(close: pd.Series, length: int = 14) -> pd.Series:
    """Ulcer Index over ``length`` bars (downside volatility; >= 0)."""
    roll_max = close.rolling(length, min_periods=length).max()
    drawdown = 100.0 * (close - roll_max) / roll_max
    return (drawdown.pow(2).rolling(length, min_periods=length).mean()).pow(0.5)


@INDICATORS.register
class UlcerIndex(Indicator):
    """Ulcer Index.

    What: RMS of percentage drawdowns from the recent high — a downside-only volatility gauge.
    Best settings: ``length`` 14.
    Edge cases: rising market (no drawdown) -> 0; first ``length-1`` bars NaN.
    Parity: pandas-ta ``ui``.
    """

    spec = IndicatorSpec(
        name="ulcer",
        category="volatility",
        aliases=("Ulcer Index", "UI"),
        inputs=(CLOSE,),
        outputs=("ulcer",),
        references=("Peter Martin", "pandas-ta ui"),
        doc="ref/ta_docs/volatility/misc_volatility.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return ulcer(df[CLOSE], self.params["length"])
