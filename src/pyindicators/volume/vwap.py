"""VWAP — Volume Weighted Average Price (rolling / window-anchored form).

``VWAP = sum(TP*Volume, N) / sum(Volume, N)`` with TP = (H+L+C)/3. We implement the
*rolling* (N-bar) form because it is causal and needs no DatetimeIndex; the classic
session-anchored VWAP (daily reset) requires intraday timestamps and is a future addition.
See ``ref/ta_docs/volume/VWAP.md``.
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


def vwap(df: pd.DataFrame, length: int = 14) -> pd.Series:
    """Rolling VWAP over ``length`` bars (typical-price weighted by volume)."""
    tp = (df[HIGH] + df[LOW] + df[CLOSE]) / 3.0
    pv = (tp * df[VOLUME]).rolling(length, min_periods=length).sum()
    vol = df[VOLUME].rolling(length, min_periods=length).sum()
    return safe_divide(pv, vol)


@INDICATORS.register
class VWAP(Indicator):
    """Volume Weighted Average Price (rolling).

    What: the volume-weighted mean of typical price over N bars — a fair-value anchor.
    Best settings: ``length`` 14 (rolling). Session-anchored VWAP needs intraday timestamps.
    Edge cases: sum(Volume) == 0 -> guarded to NaN.
    Parity: rolling form (causal); pandas-ta ``vwap`` is session-anchored (different semantics).
    """

    spec = IndicatorSpec(
        name="vwap",
        category="volume",
        aliases=("Volume Weighted Average Price",),
        inputs=(HIGH, LOW, CLOSE, VOLUME),
        outputs=("vwap",),
        references=("pandas-ta vwap (session)", "freqtrade rolling_vwap"),
        doc="ref/ta_docs/volume/VWAP.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return vwap(df, self.params["length"])
