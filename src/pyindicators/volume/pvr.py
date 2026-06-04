"""PVR — Price Volume Rank (Anthony Macek): a 1-4 classification of price/volume direction."""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, INDICATORS, VOLUME, Indicator, IndicatorSpec


def pvr(df: pd.DataFrame) -> pd.Series:
    """Price Volume Rank: 1 (P up, V up), 2 (P up, V down), 3 (P down, V up), 4 (P down, V down)."""
    cd = df[CLOSE].diff()
    vd = df[VOLUME].diff()
    rank = np.where(
        (cd >= 0) & (vd >= 0), 1.0,
        np.where((cd >= 0) & (vd < 0), 2.0, np.where((cd < 0) & (vd >= 0), 3.0, 4.0)),
    )
    out = pd.Series(rank, index=df.index)
    out.iloc[0] = np.nan  # no prior bar to compare
    return out


@INDICATORS.register
class PriceVolumeRank(Indicator):
    """Price Volume Rank.

    What: a 1-4 code combining price and volume direction (Macek's bull/bear classification).
    Best settings: none (per-bar).
    Edge cases: first bar has no prior comparison (NaN).
    Parity: pandas-ta ``pvr``.
    """

    spec = IndicatorSpec(
        name="pvr",
        category="volume",
        aliases=("Price Volume Rank",),
        inputs=(CLOSE, VOLUME),
        outputs=("pvr",),
        bounds={"pvr": (1.0, 4.0)},
        references=("Macek", "pandas-ta pvr"),
        doc="ref/ta_docs/volume/misc_volume.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return pvr(df)
