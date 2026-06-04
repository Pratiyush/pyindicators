"""MARKETFI — Market Facilitation Index (Bill Williams): ``(high - low) / volume``."""

from __future__ import annotations

import pandas as pd

from pyindicators.core import HIGH, INDICATORS, LOW, VOLUME, Indicator, IndicatorSpec, safe_divide


def marketfi(df: pd.DataFrame) -> pd.Series:
    """Market Facilitation Index = range per unit of volume."""
    return safe_divide(df[HIGH] - df[LOW], df[VOLUME])


@INDICATORS.register
class MarketFI(Indicator):
    """Market Facilitation Index.

    What: how far price moved per unit of volume — efficiency of price movement.
    Best settings: none (per-bar).
    Edge cases: zero volume -> guarded to NaN.
    Parity: tulip ``marketfi`` (validated against the explicit formula).
    """

    spec = IndicatorSpec(
        name="marketfi",
        category="volume",
        aliases=("Market Facilitation Index",),
        inputs=(HIGH, LOW, VOLUME),
        outputs=("marketfi",),
        references=("Bill Williams", "tulip marketfi"),
        doc="ref/ta_docs/volume/misc_volume.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return marketfi(df)
