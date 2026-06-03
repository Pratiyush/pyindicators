"""Rolling Standard Deviation (base / statistics primitive).

Dispersion of the last ``length`` values around their mean — the base for Bollinger Bands,
z-score, and the Relative Volatility Index. TA-Lib ``STDDEV`` uses the *population* form
(``ddof=0``); pandas defaults to *sample* (``ddof=1``). We default to population for TA-Lib
parity and expose ``ddof``. See ``ref/ta_docs/base/RollingStdev.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def stdev(series: pd.Series, length: int, ddof: int = 0) -> pd.Series:
    """Rolling standard deviation (``ddof=0`` population by default, matching TA-Lib)."""
    return series.rolling(length, min_periods=length).std(ddof=ddof)


@INDICATORS.register
class StdDev(Indicator):
    """Rolling Standard Deviation.

    What: dispersion of the last ``length`` closes around their mean (non-negative).
    Best settings: ``length`` 20 (Bollinger). ``ddof`` 0 = population (TA-Lib), 1 = sample.
    Edge cases: constant series -> 0 (downstream %B/z-score must guard /0); N=1 population = 0.
    Parity: TA-Lib ``STDDEV`` (``ddof=0``); pandas-ta ``stdev`` (``ddof=1``).
    """

    spec = IndicatorSpec(
        name="stdev",
        category="base",
        aliases=("STDDEV", "Standard Deviation", "Moving StdDev"),
        inputs=(CLOSE,),
        outputs=("stdev",),
        talib_compatible=True,
        references=("TA-Lib STDDEV", "pandas-ta stdev", "tulip stddev"),
        doc="ref/ta_docs/base/RollingStdev.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=1)
        ddof: int = Field(default=0, ge=0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return stdev(df[CLOSE], self.params["length"], self.params["ddof"])
