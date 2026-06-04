"""PSL — Psychological Line: percent of up-closes over a window (sentiment)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def psl(close: pd.Series, length: int = 12) -> pd.Series:
    """Psychological Line = 100 * (number of up-closes) / length."""
    up = (close.diff() > 0).astype("float64")
    return 100.0 * up.rolling(length, min_periods=length).sum() / length


@INDICATORS.register
class PSL(Indicator):
    """Psychological Line.

    What: the percentage of up-closes over N bars (a simple sentiment gauge, 0-100).
    Best settings: ``length`` 12; > 75 optimistic, < 25 pessimistic.
    Edge cases: first bar has no prior close (counts as not-up).
    Parity: pandas-ta ``psl``.
    """

    spec = IndicatorSpec(
        name="psl",
        category="momentum",
        aliases=("Psychological Line",),
        inputs=(CLOSE,),
        outputs=("psl",),
        bounds={"psl": (0.0, 100.0)},
        references=("pandas-ta psl",),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=12, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return psl(df[CLOSE], self.params["length"])
