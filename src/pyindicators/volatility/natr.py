"""NATR — Normalized Average True Range (volatility).

ATR expressed as a percentage of close, so it is comparable across instruments and price
levels: ``NATR = 100 * ATR / Close``. See ``ref/ta_docs/volatility/ATR_NATR.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec, safe_divide

from .atr import atr


def natr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    """Normalized ATR = 100 * ATR / Close (guarded against Close == 0)."""
    return 100.0 * safe_divide(atr(df, length), df[CLOSE])


@INDICATORS.register
class NATR(Indicator):
    """Normalized Average True Range.

    What: ATR as a percent of price — volatility comparable across symbols/price levels.
    Best settings: ``length`` 14.
    Edge cases: Close == 0 -> guarded (NaN); otherwise mirrors ATR.
    Parity: TA-Lib ``NATR`` / pandas-ta ``natr`` (up to the ATR seeding convention).
    """

    spec = IndicatorSpec(
        name="natr",
        category="volatility",
        aliases=("Normalized ATR",),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("natr",),
        talib_compatible=True,
        references=("TA-Lib NATR", "pandas-ta natr"),
        doc="ref/ta_docs/volatility/ATR_NATR.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return natr(df, self.params["length"])
