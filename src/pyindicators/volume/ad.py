"""ADL — Accumulation/Distribution Line (Marc Chaikin).

Money Flow Multiplier (intrabar close location, -1..+1) times volume, accumulated:
``MFM = ((Close-Low) - (High-Close)) / (High-Low)``; ``ADL = cumsum(MFM * Volume)``.
A High==Low bar gives MFM = 0 (not NaN). See ``ref/ta_docs/volume/ADL_CMF_Chaikin.md``.
"""

from __future__ import annotations

import pandas as pd

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


def money_flow_volume(df: pd.DataFrame) -> pd.Series:
    """Money Flow Volume = MFM * Volume (MFM is 0 on a High==Low bar)."""
    mfm = safe_divide((df[CLOSE] - df[LOW]) - (df[HIGH] - df[CLOSE]), df[HIGH] - df[LOW], fill=0.0)
    return mfm * df[VOLUME]


def ad(df: pd.DataFrame) -> pd.Series:
    """Accumulation/Distribution Line = cumulative Money Flow Volume."""
    return money_flow_volume(df).cumsum()


@INDICATORS.register
class AD(Indicator):
    """Accumulation/Distribution Line.

    What: cumulative money-flow-volume — accumulation vs distribution that confirms price.
    Best settings: none (cumulative).
    Edge cases: High==Low -> MFM 0 (not NaN); intrabar location ignores close-to-close gaps.
    Parity: TA-Lib ``AD`` / pandas-ta ``ad``.
    """

    spec = IndicatorSpec(
        name="ad",
        category="volume",
        aliases=("Accumulation/Distribution Line", "ADL"),
        inputs=(HIGH, LOW, CLOSE, VOLUME),
        outputs=("ad",),
        talib_compatible=True,
        references=("Chaikin", "TA-Lib AD", "pandas-ta ad"),
        doc="ref/ta_docs/volume/ADL_CMF_Chaikin.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return ad(df)
