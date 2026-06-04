"""CFO — Chande Forecast Oscillator: percent gap between price and its linear forecast."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide
from pyindicators.statistics.tsf import tsf


def cfo(close: pd.Series, length: int = 9) -> pd.Series:
    """Chande Forecast Oscillator = 100 * (close - TSF(close, length)) / close."""
    return 100.0 * safe_divide(close - tsf(close, length), close)


@INDICATORS.register
class CFO(Indicator):
    """Chande Forecast Oscillator.

    What: how far price sits from its time-series (linear-regression) forecast, in percent.
    Best settings: ``length`` 9; oscillates around zero.
    Edge cases: needs ``length`` >= 2 (TSF); close 0 guarded.
    Parity: pandas-ta ``cfo``.
    """

    spec = IndicatorSpec(
        name="cfo",
        category="momentum",
        aliases=("Chande Forecast Oscillator",),
        inputs=(CLOSE,),
        outputs=("cfo",),
        references=("Chande", "pandas-ta cfo"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=9, ge=2)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return cfo(df[CLOSE], self.params["length"])
