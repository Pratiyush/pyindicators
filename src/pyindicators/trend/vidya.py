"""VIDYA — Variable Index Dynamic Average (Tushar Chande).

An EMA whose smoothing is scaled bar-by-bar by the *absolute* Chande Momentum Oscillator
(in fraction form, 0..1): high momentum -> faster adaptation, chop -> slower. Stateful
recursion seeded with an SMA at the warm-up boundary. See ``ref/ta_docs/trend/misc_MA.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec
from pyindicators.momentum.cmo import cmo


def vidya(close: pd.Series, length: int = 14) -> pd.Series:
    """Variable Index Dynamic Average: alpha = 2/(length+1) scaled by |CMO| each bar."""
    alpha = 2.0 / (length + 1.0)
    # |CMO| as a 0..1 fraction (our cmo() is the [-100, 100] form -> /100). A flat window
    # makes cmo() NaN, which propagates through the recursion exactly as pandas-ta does.
    k = (cmo(close, length).abs() / 100.0).to_numpy()
    x = close.to_numpy(dtype="float64")
    n = x.size
    out = np.full(n, np.nan)
    if n < length:
        return pd.Series(out, index=close.index)
    out[length - 1] = x[:length].mean()  # SMA seed at the warm-up boundary
    for i in range(length, n):
        out[i] = alpha * k[i] * x[i] + out[i - 1] * (1.0 - alpha * k[i])
    return pd.Series(out, index=close.index)


@INDICATORS.register
class VIDYA(Indicator):
    """Variable Index Dynamic Average.

    What: an adaptive EMA that speeds up when |CMO| (momentum) is high and slows in chop.
    Best settings: ``length`` 14; rising VIDYA = trend, flat = range.
    Edge cases: flat window -> CMO NaN -> NaN propagates (matches pandas-ta); first
        ``length`` bars NaN (SMA-seeded at ``length - 1``).
    Parity: pandas-ta ``vidya`` (CMO-fraction variant), exact.
    """

    spec = IndicatorSpec(
        name="vidya",
        category="trend",
        aliases=("Variable Index Dynamic Average",),
        inputs=(CLOSE,),
        outputs=("vidya",),
        stateful=True,
        references=("Chande", "pandas-ta vidya"),
        doc="ref/ta_docs/trend/misc_MA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return vidya(df[CLOSE], self.params["length"])
