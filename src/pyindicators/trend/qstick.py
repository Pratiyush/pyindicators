"""QStick — Tushar Chande: ``SMA(close - open, N)`` — candle-body momentum."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import CLOSE, INDICATORS, OPEN, Indicator, IndicatorSpec


def qstick(df: pd.DataFrame, length: int = 10) -> pd.Series:
    """QStick = SMA of (close - open) over ``length`` bars."""
    return sma(df[CLOSE] - df[OPEN], length)


@INDICATORS.register
class QStick(Indicator):
    """QStick.

    What: the average candle body (close - open) over N bars; > 0 = bullish pressure.
    Best settings: ``length`` 10.
    Edge cases: first ``length-1`` bars NaN.
    Parity: pandas-ta ``qstick``.
    """

    spec = IndicatorSpec(
        name="qstick",
        category="trend",
        aliases=("QStick",),
        inputs=(OPEN, CLOSE),
        outputs=("qstick",),
        references=("Chande", "pandas-ta qstick"),
        doc="ref/ta_docs/trend/README.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=10, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return qstick(df, self.params["length"])
