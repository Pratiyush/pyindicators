"""ALMA — Arnaud Legoux Moving Average: a Gaussian-weighted MA with an offset.

Weights ``w[i] = exp(-(i - m)^2 / (2 s^2))`` with ``m = offset*(N-1)``, ``s = N/sigma``,
trading off lag (offset) vs smoothness (sigma). See ``ref/ta_docs/trend/misc_MA.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from ._weighted import weighted_ma


def alma(close: pd.Series, length: int = 10, sigma: float = 6.0, offset: float = 0.85) -> pd.Series:
    """Arnaud Legoux MA (Gaussian-weighted with an offset)."""
    m = offset * (length - 1)
    s = length / sigma
    i = np.arange(length)
    weights = np.exp(-((i - m) ** 2) / (2.0 * s * s))
    return weighted_ma(close, weights)


@INDICATORS.register
class ALMA(Indicator):
    """Arnaud Legoux Moving Average.

    What: a Gaussian-weighted MA; ``offset`` shifts toward responsiveness, ``sigma`` smooths.
    Best settings: ``length`` 10, ``sigma`` 6, ``offset`` 0.85.
    Edge cases: first ``length-1`` bars NaN.
    Parity: canonical TradingView/Legoux weighting (offset emphasises recent bars). pandas-ta
    reverses the weight vector, so it diverges from this canonical orientation.
    """

    spec = IndicatorSpec(
        name="alma",
        category="trend",
        aliases=("Arnaud Legoux MA",),
        inputs=(CLOSE,),
        outputs=("alma",),
        references=("Legoux", "pandas-ta alma"),
        doc="ref/ta_docs/trend/misc_MA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=10, ge=1)
        sigma: float = Field(default=6.0, gt=0)
        offset: float = Field(default=0.85, ge=0, le=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        p = self.params
        return alma(df[CLOSE], p["length"], p["sigma"], p["offset"])
