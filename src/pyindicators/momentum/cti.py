"""CTI — Correlation Trend Indicator (John Ehlers, 2020).

The Pearson correlation between price and a straight time line over the window: +1 = prices
track a perfectly rising line, -1 a falling one, ~0 = no linear trend. A bounded, low-lag trend
gauge (it is ``linreg(..., r=True)`` in pandas-ta). See ``ref/ta_docs/momentum/misc_momentum.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def cti(close: pd.Series, length: int = 12) -> pd.Series:
    """Correlation Trend Indicator: rolling Pearson r of close vs a time ramp (-1..1)."""
    xd = np.arange(length, dtype="float64")
    xd -= xd.mean()
    sxx = float((xd * xd).sum())

    def _r(w: np.ndarray) -> float:
        yd = w - w.mean()
        syy = float((yd * yd).sum())
        if syy <= 0.0:  # flat window -> correlation undefined
            return np.nan
        return float((xd * yd).sum() / np.sqrt(sxx * syy))

    return close.rolling(length, min_periods=length).apply(_r, raw=True)


@INDICATORS.register
class CTI(Indicator):
    """Correlation Trend Indicator.

    What: how closely price follows a straight line over N bars (Pearson r, -1..+1).
    Best settings: ``length`` 12; > 0.5 strong up-trend, < -0.5 strong down-trend, ~0 = chop.
    Edge cases: flat window (zero price variance) -> undefined -> NaN; first ``length-1`` NaN.
    Parity: pandas-ta ``cti`` (= linreg r).
    """

    spec = IndicatorSpec(
        name="cti",
        category="momentum",
        aliases=("Correlation Trend Indicator", "Ehlers CTI"),
        inputs=(CLOSE,),
        outputs=("cti",),
        bounds={"cti": (-1.0, 1.0)},
        references=("Ehlers 2020", "pandas-ta cti"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=12, ge=2)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return cti(df[CLOSE], self.params["length"])
