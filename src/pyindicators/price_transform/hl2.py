"""hl2 / MEDPRICE — median price ``(high + low) / 2`` (price transform)."""

from __future__ import annotations

import pandas as pd

from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def hl2(df: pd.DataFrame) -> pd.Series:
    """Median price: (high + low) / 2."""
    return (df[HIGH] + df[LOW]) / 2.0


@INDICATORS.register
class HL2(Indicator):
    """Median Price (hl2).

    What: the midpoint of the bar's range; a smoother price proxy than close.
    Best settings: none (per-bar transform).
    Edge cases: none (exact, no warm-up).
    Parity: TA-Lib ``MEDPRICE`` / pandas-ta ``hl2``.
    """

    spec = IndicatorSpec(
        name="hl2",
        category="price_transform",
        aliases=("MEDPRICE", "Median Price"),
        inputs=(HIGH, LOW),
        outputs=("hl2",),
        talib_compatible=True,
        references=("TA-Lib MEDPRICE", "pandas-ta hl2"),
        doc="ref/ta_docs/price_transform/price_transforms.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return hl2(df)
