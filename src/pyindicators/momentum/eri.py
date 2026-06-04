"""Elder Ray Index (ERI) — Bull Power & Bear Power (Alexander Elder).

``Bull Power = High - EMA(close, N)``; ``Bear Power = Low - EMA(close, N)``. Composes
``base.ema``. See ``ref/ta_docs/momentum/misc_momentum.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def eri(df: pd.DataFrame, length: int = 13) -> dict:
    """Elder Ray bull power (high - EMA) and bear power (low - EMA)."""
    e = ema(df[CLOSE], length)
    return {"bull_power": df[HIGH] - e, "bear_power": df[LOW] - e}


@INDICATORS.register
class ElderRay(Indicator):
    """Elder Ray Index.

    What: buying vs selling pressure relative to an EMA (bull power, bear power).
    Best settings: ``length`` 13; bull > 0 & rising = strength, bear < 0 & falling = weakness.
    Edge cases: inherits EMA warm-up.
    Parity: pandas-ta ``eri`` (BULLP / BEARP).
    """

    spec = IndicatorSpec(
        name="eri",
        category="momentum",
        aliases=("Elder Ray", "Bull/Bear Power"),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("bull_power", "bear_power"),
        references=("Elder", "pandas-ta eri"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=13, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        return eri(df, self.params["length"])
