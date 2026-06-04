"""CMF — Chaikin Money Flow (Marc Chaikin).

``CMF = sum(Money Flow Volume, N) / sum(Volume, N)`` over N bars, bounded [-1, 1].
Composes ``volume.ad.money_flow_volume``. See ``ref/ta_docs/volume/ADL_CMF_Chaikin.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import (
    CLOSE,
    HIGH,
    INDICATORS,
    LOW,
    VOLUME,
    Indicator,
    IndicatorSpec,
    safe_divide,
)

from .ad import money_flow_volume


def cmf(df: pd.DataFrame, length: int = 20) -> pd.Series:
    """Chaikin Money Flow over ``length`` bars (bounded [-1, 1])."""
    mfv = money_flow_volume(df)
    vol_sum = df[VOLUME].rolling(length, min_periods=length).sum()
    return safe_divide(mfv.rolling(length, min_periods=length).sum(), vol_sum)


@INDICATORS.register
class CMF(Indicator):
    """Chaikin Money Flow.

    What: net money-flow volume over N bars as a fraction of total volume ([-1, 1]).
    Best settings: ``length`` 20 or 21; > 0 accumulation, < 0 distribution.
    Edge cases: sum(Volume) == 0 -> guarded to NaN; High==Low bars contribute 0.
    Parity: pandas-ta ``cmf`` (not in core TA-Lib).
    """

    spec = IndicatorSpec(
        name="cmf",
        category="volume",
        aliases=("Chaikin Money Flow",),
        inputs=(HIGH, LOW, CLOSE, VOLUME),
        outputs=("cmf",),
        bounds={"cmf": (-1.0, 1.0)},
        references=("Chaikin", "pandas-ta cmf"),
        doc="ref/ta_docs/volume/ADL_CMF_Chaikin.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return cmf(df, self.params["length"])
