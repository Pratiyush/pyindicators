"""RVOL — Relative Volume: current volume vs its trailing average (breakout gate)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import INDICATORS, VOLUME, Indicator, IndicatorSpec, safe_divide

from .vol_sma import vol_sma


def rvol(df: pd.DataFrame, length: int = 50) -> pd.Series:
    """Relative volume = volume / SMA(volume, length)."""
    return safe_divide(df[VOLUME], vol_sma(df, length))


@INDICATORS.register
class RVOL(Indicator):
    """Relative Volume.

    What: today's volume as a multiple of average volume; a breakout-confirmation gate.
    Best settings: ``length`` 50; >= ~1.4 confirms a breakout (O'Neil/Carter).
    Edge cases: zero average volume guarded; first ``length-1`` bars NaN.
    Parity: volume / SMA(volume) (validated against the explicit formula).
    """

    spec = IndicatorSpec(
        name="rvol",
        category="volume",
        aliases=("Relative Volume",),
        inputs=(VOLUME,),
        outputs=("rvol",),
        references=("O'Neil", "Carter"),
        doc="ref/ta_docs/volume/misc_volume.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=50, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return rvol(df, self.params["length"])
