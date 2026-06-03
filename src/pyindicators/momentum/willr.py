"""Williams %R — momentum oscillator (Larry Williams).

Like the Stochastic %K but inverted and scaled to [-100, 0]:
``%R = -100 * (HH(N) - Close) / (HH(N) - LL(N))``. 0 = close at the top of the range,
-100 = bottom. See ``ref/ta_docs/momentum/WilliamsR.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec, safe_divide


def willr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    """Williams %R over ``length`` bars, bounded [-100, 0]."""
    hh = df[HIGH].rolling(length, min_periods=length).max()
    ll = df[LOW].rolling(length, min_periods=length).min()
    return safe_divide(-100.0 * (hh - df[CLOSE]), hh - ll)  # NaN where HH == LL


@INDICATORS.register
class WilliamsR(Indicator):
    """Williams %R.

    What: where the close sits in the N-bar range, inverted, scaled [-100, 0].
    Best settings: 14; bands -20 overbought, -80 oversold.
    Edge cases: HH == LL (flat window) -> guarded to NaN.
    Parity: TA-Lib ``WILLR`` / pandas-ta ``willr``.
    """

    spec = IndicatorSpec(
        name="willr",
        category="momentum",
        aliases=("Williams %R", "Williams Percent Range"),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("willr",),
        bounds={"willr": (-100.0, 0.0)},
        talib_compatible=True,
        references=("Williams", "TA-Lib WILLR", "pandas-ta willr"),
        doc="ref/ta_docs/momentum/WilliamsR.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return willr(df, self.params["length"])
