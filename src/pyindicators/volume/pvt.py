"""PVT — Price Volume Trend.

Like OBV but scaled by the percent price change:
``PVT_t = PVT_{t-1} + Volume_t * (Close_t - Close_{t-1}) / Close_{t-1}`` (cumulative).
See ``ref/ta_docs/volume/misc_volume.md``.
"""

from __future__ import annotations

import pandas as pd

from pyindicators.core import CLOSE, INDICATORS, VOLUME, Indicator, IndicatorSpec


def pvt(df: pd.DataFrame) -> pd.Series:
    """Price Volume Trend (cumulative percent-change-weighted volume)."""
    delta = df[CLOSE].pct_change() * df[VOLUME]
    delta.iloc[0] = 0.0  # no prior close; seed the cumulative sum at 0
    return delta.cumsum()


@INDICATORS.register
class PVT(Indicator):
    """Price Volume Trend.

    What: cumulative volume weighted by percent price change — a volume-confirmation line.
    Best settings: none (cumulative); compare its trend to price.
    Edge cases: Close_{t-1} == 0 -> guarded; the first bar seeds at 0.
    Parity: pandas-ta ``pvt`` (not in core TA-Lib).
    """

    spec = IndicatorSpec(
        name="pvt",
        category="volume",
        aliases=("Price Volume Trend",),
        inputs=(CLOSE, VOLUME),
        outputs=("pvt",),
        references=("pandas-ta pvt",),
        doc="ref/ta_docs/volume/misc_volume.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return pvt(df)
