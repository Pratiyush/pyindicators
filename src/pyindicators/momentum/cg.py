"""CG — Center of Gravity (John Ehlers): a low-lag oscillator of weighted price position."""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide


def cg(close: pd.Series, length: int = 10) -> pd.Series:
    """Center of Gravity over ``length`` bars (Ehlers): -sum(weighted price)/sum(price)."""
    coefficients = np.arange(1, length + 1, dtype="float64")  # newest..oldest weights 1..N
    num = close.rolling(length, min_periods=length).apply(
        lambda x: float(np.dot(coefficients, x[::-1])), raw=True
    )
    den = close.rolling(length, min_periods=length).sum()
    return -safe_divide(num, den)


@INDICATORS.register
class CenterOfGravity(Indicator):
    """Center of Gravity.

    What: Ehlers' low-lag oscillator from the weighted "balance point" of recent prices.
    Best settings: ``length`` 10.
    Edge cases: zero price sum guarded; first ``length-1`` bars NaN.
    Parity: pandas-ta ``cg``.
    """

    spec = IndicatorSpec(
        name="cg",
        category="momentum",
        aliases=("Center of Gravity",),
        inputs=(CLOSE,),
        outputs=("cg",),
        references=("Ehlers", "pandas-ta cg"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=10, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return cg(df[CLOSE], self.params["length"])
