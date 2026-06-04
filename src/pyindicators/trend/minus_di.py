"""-DI — Minus Directional Indicator (the bearish leg of DMI; Wilder)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec

from .adx import directional_movement


def minus_di(df: pd.DataFrame, length: int = 14) -> pd.Series:
    """-DI over ``length`` bars (bearish directional movement, 0-100)."""
    return directional_movement(df, length)["minus_di"]


@INDICATORS.register
class MinusDI(Indicator):
    """Minus Directional Indicator (-DI).

    What: smoothed downward directional movement as a percent of true range (0-100).
    Best settings: ``length`` 14; -DI above +DI = bearish.
    Edge cases: inside bars contribute 0 (-DM=0).
    Parity: matches pandas-ta -DI exactly; TA-Lib differs only in the Wilder seed (converges).
    """

    spec = IndicatorSpec(
        name="minus_di",
        category="trend",
        aliases=("-DI", "Minus Directional Indicator"),
        inputs=(HIGH, LOW, "close"),
        outputs=("minus_di",),
        bounds={"minus_di": (0.0, 100.0)},
        talib_compatible=True,
        references=("Wilder 1978", "TA-Lib MINUS_DI", "pandas-ta adx"),
        doc="ref/ta_docs/trend/ADX_DMI.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return minus_di(df, self.params["length"])
