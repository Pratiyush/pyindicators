"""+DM — Plus Directional Movement (the raw Wilder-smoothed up-move; Wilder 1978).

The bullish leg of DMI *before* it is divided by ATR to form +DI. Up-move (``high.diff()``)
counts only when it both exceeds the down-move and is positive; the result is Wilder-smoothed
and rescaled to the running sum (``length * RMA``). See ``ref/ta_docs/trend/ADX_DMI.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import rma
from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def plus_dm(df: pd.DataFrame, length: int = 14) -> pd.Series:
    """Plus Directional Movement: ``length * RMA(+DM)`` over ``length`` bars."""
    up = df[HIGH].diff()
    down = -df[LOW].diff()
    pdm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=df.index)
    pdm.iloc[0] = np.nan  # no directional movement on the first bar
    return length * rma(pdm, length)


@INDICATORS.register
class PlusDM(Indicator):
    """Plus Directional Movement (+DM).

    What: the raw smoothed upward directional movement (price units), the +DI numerator.
    Best settings: ``length`` 14 (Wilder).
    Edge cases: inside bars contribute 0; the first bar is NaN (no prior to diff).
    Parity: pandas-ta ``plus_dm`` exactly; TA-Lib ``PLUS_DM`` differs only in the Wilder seed
        (it converges).
    """

    spec = IndicatorSpec(
        name="plus_dm",
        category="trend",
        aliases=("+DM", "Plus Directional Movement"),
        inputs=(HIGH, LOW),
        outputs=("plus_dm",),
        talib_compatible=True,
        references=("Wilder 1978", "TA-Lib PLUS_DM", "pandas-ta plus_dm"),
        doc="ref/ta_docs/trend/ADX_DMI.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return plus_dm(df, self.params["length"])
