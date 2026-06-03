"""CCI — Commodity Channel Index (momentum, Donald Lambert 1980).

How far typical price is from its SMA, in units of mean absolute deviation:
``CCI = (TP - SMA(TP)) / (0.015 * MAD(TP))``. The 0.015 constant calibrates ~70-80% of
values into +/-100. Composes ``base.sma``. See ``ref/ta_docs/momentum/CCI.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec, safe_divide


def _mean_abs_dev(window: np.ndarray) -> float:
    return float(np.abs(window - window.mean()).mean())


def cci(df: pd.DataFrame, length: int = 20, c: float = 0.015) -> pd.Series:
    """Commodity Channel Index over ``length`` bars (flat typical price -> 0)."""
    tp = (df[HIGH] + df[LOW] + df[CLOSE]) / 3.0
    sma_tp = sma(tp, length)
    mad = tp.rolling(length, min_periods=length).apply(_mean_abs_dev, raw=True)
    return safe_divide(tp - sma_tp, c * mad, fill=0.0)  # MAD == 0 (flat) -> CCI 0


@INDICATORS.register
class CCI(Indicator):
    """Commodity Channel Index.

    What: deviation of typical price from its SMA, scaled by mean absolute deviation.
    Best settings: 20, constant 0.015 (Lambert); +/-100 = strong/overbought-oversold.
    Edge cases: MAD == 0 (flat typical price) -> CCI 0.
    Parity: TA-Lib ``CCI`` / pandas-ta ``cci``.
    """

    spec = IndicatorSpec(
        name="cci",
        category="momentum",
        aliases=("Commodity Channel Index",),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("cci",),
        talib_compatible=True,
        references=("Lambert 1980", "TA-Lib CCI", "pandas-ta cci"),
        doc="ref/ta_docs/momentum/CCI.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=1)
        c: float = Field(default=0.015, gt=0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return cci(df, self.params["length"], self.params["c"])
