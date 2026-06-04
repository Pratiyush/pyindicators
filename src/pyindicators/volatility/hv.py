"""Historical Volatility (HV) — annualised realised volatility of log returns.

``HV = stdev(ln(close/close_{t-1}), N) * sqrt(annual) * 100``. See
``ref/ta_docs/volatility/misc_volatility.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def hv(close: pd.Series, length: int = 20, annual: int = 252) -> pd.Series:
    """Annualised historical (realised) volatility in percent."""
    log_ret = np.log(close / close.shift(1))
    return log_ret.rolling(length, min_periods=length).std(ddof=1) * np.sqrt(annual) * 100.0


@INDICATORS.register
class HistoricalVolatility(Indicator):
    """Historical Volatility.

    What: annualised standard deviation of log returns (realised volatility, in percent).
    Best settings: ``length`` 20, ``annual`` 252 (daily bars).
    Edge cases: constant series -> 0; needs >= 2 returns for sample stdev.
    Parity: standard realised-volatility formula (validated against the explicit definition).
    """

    spec = IndicatorSpec(
        name="hv",
        category="volatility",
        aliases=("Historical Volatility", "Realised Volatility"),
        inputs=(CLOSE,),
        outputs=("hv",),
        references=("Landry", "standard realised volatility"),
        doc="ref/ta_docs/volatility/misc_volatility.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=2)
        annual: int = Field(default=252, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return hv(df[CLOSE], self.params["length"], self.params["annual"])
