"""PVOL — Price-Volume: ``close * volume`` per bar (raw dollar volume)."""

from __future__ import annotations

import pandas as pd

from pyindicators.core import CLOSE, INDICATORS, VOLUME, Indicator, IndicatorSpec


def pvol(df: pd.DataFrame) -> pd.Series:
    """Price times volume per bar."""
    return df[CLOSE] * df[VOLUME]


@INDICATORS.register
class PVOL(Indicator):
    """Price-Volume.

    What: close times volume — a raw measure of the money traded each bar.
    Best settings: none (per-bar).
    Edge cases: none.
    Parity: pandas-ta ``pvol``.
    """

    spec = IndicatorSpec(
        name="pvol",
        category="volume",
        aliases=("Price-Volume",),
        inputs=(CLOSE, VOLUME),
        outputs=("pvol",),
        references=("pandas-ta pvol",),
        doc="ref/ta_docs/volume/misc_volume.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return pvol(df)
