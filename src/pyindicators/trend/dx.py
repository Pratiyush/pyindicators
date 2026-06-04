"""DX — Directional Movement Index (the un-smoothed precursor to ADX; Wilder)."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec

from .adx import directional_movement


def dx(df: pd.DataFrame, length: int = 14) -> pd.Series:
    """DX = 100 * |+DI - -DI| / (+DI + -DI) over ``length`` bars (0-100)."""
    return directional_movement(df, length)["dx"]


@INDICATORS.register
class DX(Indicator):
    """Directional Movement Index (DX).

    What: the normalised spread between +DI and -DI (0-100); ADX is its Wilder average.
    Best settings: ``length`` 14.
    Edge cases: +DI + -DI == 0 -> guarded to NaN.
    Parity: TA-Lib ``DX`` (converges; Wilder seed differs early).
    """

    spec = IndicatorSpec(
        name="dx",
        category="trend",
        aliases=("Directional Movement Index",),
        inputs=(HIGH, LOW, "close"),
        outputs=("dx",),
        bounds={"dx": (0.0, 100.0)},
        talib_compatible=True,
        references=("Wilder 1978", "TA-Lib DX"),
        doc="ref/ta_docs/trend/ADX_DMI.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return dx(df, self.params["length"])
