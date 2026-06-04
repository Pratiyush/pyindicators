"""-DM — Minus Directional Movement (the raw Wilder-smoothed down-move; Wilder 1978).

The bearish leg of DMI *before* it is divided by ATR to form -DI. Down-move
(``-low.diff()``) counts only when it both exceeds the up-move and is positive; the result is
Wilder-smoothed and rescaled to the running sum (``length * RMA``). See
``ref/ta_docs/trend/ADX_DMI.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import rma
from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def minus_dm(df: pd.DataFrame, length: int = 14) -> pd.Series:
    """Minus Directional Movement: ``length * RMA(-DM)`` over ``length`` bars."""
    up = df[HIGH].diff()
    down = -df[LOW].diff()
    mdm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=df.index)
    mdm.iloc[0] = np.nan  # no directional movement on the first bar
    return length * rma(mdm, length)


@INDICATORS.register
class MinusDM(Indicator):
    """Minus Directional Movement (-DM).

    What: the raw smoothed downward directional movement (price units), the -DI numerator.
    Best settings: ``length`` 14 (Wilder).
    Edge cases: inside bars contribute 0; the first bar is NaN (no prior to diff).
    Parity: pandas-ta ``minus_dm`` exactly; TA-Lib ``MINUS_DM`` differs only in the Wilder
        seed (it converges).
    """

    spec = IndicatorSpec(
        name="minus_dm",
        category="trend",
        aliases=("-DM", "Minus Directional Movement"),
        inputs=(HIGH, LOW),
        outputs=("minus_dm",),
        talib_compatible=True,
        references=("Wilder 1978", "TA-Lib MINUS_DM", "pandas-ta minus_dm"),
        doc="ref/ta_docs/trend/ADX_DMI.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return minus_dm(df, self.params["length"])
