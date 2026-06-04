"""ADXR — Average Directional Index Rating: ``(ADX_t + ADX_{t-N}) / 2`` (Wilder)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec

from .adx import directional_movement


def adxr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    """ADXR = average of current ADX and ADX ``length`` bars ago."""
    return directional_movement(df, length)["adxr"]


@INDICATORS.register
class ADXR(Indicator):
    """Average Directional Index Rating (ADXR).

    What: a smoothed trend-strength rating (averages ADX now with ADX N bars ago).
    Best settings: ``length`` 14.
    Edge cases: needs ~2x the ADX warm-up; converges to TA-Lib on the tail.
    Parity: TA-Lib ``ADXR`` (converges; Wilder seed differs early).
    """

    spec = IndicatorSpec(
        name="adxr",
        category="trend",
        aliases=("Average Directional Index Rating",),
        inputs=(HIGH, LOW, "close"),
        outputs=("adxr",),
        bounds={"adxr": (0.0, 100.0)},
        talib_compatible=True,
        references=("Wilder 1978", "TA-Lib ADXR"),
        doc="ref/ta_docs/trend/ADX_DMI.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return adxr(df, self.params["length"])
