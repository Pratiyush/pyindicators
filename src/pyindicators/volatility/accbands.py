"""Acceleration Bands (ACCBANDS) — Price Headley.

``Upper = SMA(high * (1 + c*(H-L)/(H+L)), N)``; ``Lower = SMA(low * (1 - c*(H-L)/(H+L)), N)``;
``Mid = SMA(close, N)``. Composes ``base.sma``. See ``ref/ta_docs/volatility/misc_volatility.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec, safe_divide


def accbands(df: pd.DataFrame, length: int = 20, c: float = 4.0) -> dict:
    """Acceleration Bands lower/mid/upper over ``length`` bars."""
    hl_ratio = c * safe_divide(df[HIGH] - df[LOW], df[HIGH] + df[LOW])
    upper = sma(df[HIGH] * (1.0 + hl_ratio), length)
    lower = sma(df[LOW] * (1.0 - hl_ratio), length)
    mid = sma(df[CLOSE], length)
    return {"accbands_lower": lower, "accbands_mid": mid, "accbands_upper": upper}


@INDICATORS.register
class AccelerationBands(Indicator):
    """Acceleration Bands.

    What: SMA-smoothed envelope whose width scales with the high-low range ratio.
    Best settings: ``length`` 20, ``c`` 4.
    Edge cases: High+Low == 0 -> guarded (prices are positive in practice).
    Parity: pandas-ta ``accbands`` / TA-Lib ``ACCBANDS``.
    """

    spec = IndicatorSpec(
        name="accbands",
        category="volatility",
        aliases=("Acceleration Bands", "ACCBANDS"),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("accbands_lower", "accbands_mid", "accbands_upper"),
        references=("Headley", "pandas-ta accbands", "TA-Lib ACCBANDS"),
        doc="ref/ta_docs/volatility/misc_volatility.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=1)
        c: float = Field(default=4.0, gt=0)

    def _compute(self, df: pd.DataFrame) -> dict:
        return accbands(df, self.params["length"], self.params["c"])
