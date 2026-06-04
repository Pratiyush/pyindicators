"""hlc3 / TYPPRICE — typical price ``(high + low + close) / 3`` (price transform)."""

from __future__ import annotations

import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def hlc3(df: pd.DataFrame) -> pd.Series:
    """Typical price: (high + low + close) / 3."""
    return (df[HIGH] + df[LOW] + df[CLOSE]) / 3.0


@INDICATORS.register
class HLC3(Indicator):
    """Typical Price (hlc3).

    What: average of high, low, and close; the input to CCI and Money Flow.
    Best settings: none (per-bar transform).
    Edge cases: none (exact, no warm-up).
    Parity: TA-Lib ``TYPPRICE`` / pandas-ta ``hlc3``.
    """

    spec = IndicatorSpec(
        name="hlc3",
        category="price_transform",
        aliases=("TYPPRICE", "Typical Price"),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("hlc3",),
        talib_compatible=True,
        references=("TA-Lib TYPPRICE", "pandas-ta hlc3"),
        doc="ref/ta_docs/price_transform/price_transforms.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return hlc3(df)
