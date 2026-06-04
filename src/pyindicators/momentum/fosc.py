"""FOSC — Forecast Oscillator (Tushar Chande).

The percentage gap between price and its time-series forecast (the linear-regression value
projected one bar ahead): ``100 * (close - TSF) / close``. Positive = price above its own
trend forecast (momentum up), persistent sign = a trend. Composes ``statistics.tsf``. See
``ref/ta_docs/momentum/misc_momentum.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide
from pyindicators.statistics.tsf import tsf


def fosc(close: pd.Series, length: int = 14) -> pd.Series:
    """Forecast Oscillator: 100 * (close - TSF(close, length)) / close."""
    return 100.0 * safe_divide(close - tsf(close, length), close)


@INDICATORS.register
class FOSC(Indicator):
    """Forecast Oscillator.

    What: how far price sits from its own one-bar-ahead regression forecast, in percent.
    Best settings: ``length`` 14; oscillates around 0 — large |FOSC| = price diverging from its
        forecast (the next-bar TSF leads price, so a steady trend shows a small offset, not 0).
    Edge cases: close == 0 -> guarded to NaN; first ``length-1`` bars NaN (regression warm-up).
    Parity: pandas-ta ``fosc`` (= 100*(close - linreg tsf)/close); only pandas-ta ships it.
    """

    spec = IndicatorSpec(
        name="fosc",
        category="momentum",
        aliases=("Forecast Oscillator",),
        inputs=(CLOSE,),
        outputs=("fosc",),
        references=("Chande", "pandas-ta fosc"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=2)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return fosc(df[CLOSE], self.params["length"])
