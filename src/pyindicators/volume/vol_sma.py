"""Volume SMA — simple moving average of volume (baseline for RVOL / VPA thresholds)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import INDICATORS, VOLUME, Indicator, IndicatorSpec


def vol_sma(df: pd.DataFrame, length: int = 50) -> pd.Series:
    """Simple moving average of volume over ``length`` bars."""
    return sma(df[VOLUME], length)


@INDICATORS.register
class VolumeSMA(Indicator):
    """Volume SMA.

    What: the average traded volume over ``length`` bars — the baseline "normal" volume.
    Best settings: ``length`` 50 (IBD); the denominator for relative volume.
    Edge cases: first ``length-1`` bars NaN.
    Parity: TA-Lib ``SMA`` applied to volume.
    """

    spec = IndicatorSpec(
        name="vol_sma",
        category="volume",
        aliases=("Volume SMA", "Average Volume"),
        inputs=(VOLUME,),
        outputs=("vol_sma",),
        talib_compatible=True,
        references=("IBD", "TA-Lib SMA"),
        doc="ref/ta_docs/volume/misc_volume.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=50, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return vol_sma(df, self.params["length"])
