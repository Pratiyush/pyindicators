"""MFI — Money Flow Index (volume-weighted RSI).

RSI-like oscillator on typical-price money flow:
``MFI = 100 - 100 / (1 + sum(PosMF, N) / sum(NegMF, N))`` where money flow = TP*Volume split
by the sign of the TP change. See ``ref/ta_docs/volume/MFI.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, VOLUME, Indicator, IndicatorSpec


def mfi(df: pd.DataFrame, length: int = 14) -> pd.Series:
    """Money Flow Index over ``length`` bars, bounded [0, 100]."""
    tp = (df[HIGH] + df[LOW] + df[CLOSE]) / 3.0
    raw_mf = tp * df[VOLUME]
    delta = tp.diff()
    pos = raw_mf.where(delta > 0, 0.0)
    neg = raw_mf.where(delta < 0, 0.0)
    pos.iloc[0] = np.nan  # no TP change on the first bar (exclude from the sums)
    neg.iloc[0] = np.nan
    pos_sum = pos.rolling(length, min_periods=length).sum()
    neg_sum = neg.rolling(length, min_periods=length).sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = pos_sum / neg_sum  # NegMF 0 -> inf -> MFI 100; both 0 -> NaN
        return 100.0 - 100.0 / (1.0 + ratio)


@INDICATORS.register
class MFI(Indicator):
    """Money Flow Index.

    What: a volume-weighted RSI of typical-price money flow (0-100).
    Best settings: ``length`` 14; bands 80/20; divergence.
    Edge cases: sum(NegMF) 0 -> 100; unchanged TP excluded; fully flat window -> NaN.
    Parity: TA-Lib ``MFI`` / pandas-ta ``mfi``.
    """

    spec = IndicatorSpec(
        name="mfi",
        category="volume",
        aliases=("Money Flow Index",),
        inputs=(HIGH, LOW, CLOSE, VOLUME),
        outputs=("mfi",),
        bounds={"mfi": (0.0, 100.0)},
        talib_compatible=True,
        references=("TA-Lib MFI", "pandas-ta mfi"),
        doc="ref/ta_docs/volume/MFI.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return mfi(df, self.params["length"])
