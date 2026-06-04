"""Ease of Movement (EOM) — Richard Arms.

Relates price movement to volume: ``distance = hl2.diff()``; ``box = (Volume/divisor) /
(High-Low)``; ``EOM = SMA(distance / box, length)``. High volume / small move -> low EOM.
Composes ``base.sma``. See ``ref/ta_docs/volume/misc_volume.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import HIGH, INDICATORS, LOW, VOLUME, Indicator, IndicatorSpec, safe_divide


def eom(df: pd.DataFrame, length: int = 14, divisor: float = 100_000_000.0) -> pd.Series:
    """Ease of Movement over ``length`` bars."""
    hl2 = (df[HIGH] + df[LOW]) / 2.0
    distance = hl2.diff()
    box = safe_divide(df[VOLUME] / divisor, df[HIGH] - df[LOW])  # H==L -> NaN
    emv = safe_divide(distance, box)
    return sma(emv, length)


@INDICATORS.register
class EaseOfMovement(Indicator):
    """Ease of Movement.

    What: how easily price moves relative to volume; > 0 rising on light volume = easy advance.
    Best settings: ``length`` 14, divisor 1e8.
    Edge cases: High==Low (zero range) or zero volume -> guarded to NaN.
    Parity: pandas-ta ``eom`` (not in core TA-Lib).
    """

    spec = IndicatorSpec(
        name="eom",
        category="volume",
        aliases=("Ease of Movement", "EMV"),
        inputs=(HIGH, LOW, VOLUME),
        outputs=("eom",),
        references=("Arms", "pandas-ta eom"),
        doc="ref/ta_docs/volume/misc_volume.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)
        divisor: float = Field(default=100_000_000.0, gt=0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return eom(df, self.params["length"], self.params["divisor"])
