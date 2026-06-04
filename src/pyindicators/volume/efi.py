"""Force Index (EFI) — Alexander Elder.

``EFI = EMA( (Close - Close_{t-1}) * Volume, length )``: combines price change direction,
magnitude, and volume. Composes ``base.ema``. See ``ref/ta_docs/volume/misc_volume.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import CLOSE, INDICATORS, VOLUME, Indicator, IndicatorSpec


def efi(df: pd.DataFrame, length: int = 13) -> pd.Series:
    """Elder's Force Index = EMA of (close change * volume) over ``length`` bars."""
    raw = df[CLOSE].diff() * df[VOLUME]
    return ema(raw, length)


@INDICATORS.register
class ForceIndex(Indicator):
    """Force Index (Elder).

    What: EMA-smoothed (price change x volume) — the power behind a move.
    Best settings: ``length`` 13 (Elder); 2 for short-term.
    Edge cases: first bar has no prior close (NaN); inherits EMA warm-up.
    Parity: pandas-ta ``efi`` (not in core TA-Lib).
    """

    spec = IndicatorSpec(
        name="efi",
        category="volume",
        aliases=("Force Index", "Elder Force Index"),
        inputs=(CLOSE, VOLUME),
        outputs=("efi",),
        references=("Elder", "pandas-ta efi"),
        doc="ref/ta_docs/volume/misc_volume.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=13, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return efi(df, self.params["length"])
