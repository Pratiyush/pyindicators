"""wcp / WCLPRICE — weighted close ``(high + low + 2*close) / 4`` (price transform)."""

from __future__ import annotations

import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def wcp(df: pd.DataFrame) -> pd.Series:
    """Weighted close price: (high + low + 2*close) / 4."""
    return (df[HIGH] + df[LOW] + 2.0 * df[CLOSE]) / 4.0


@INDICATORS.register
class WCP(Indicator):
    """Weighted Close Price (wcp).

    What: a price proxy that double-weights the close.
    Best settings: none (per-bar transform).
    Edge cases: none (exact, no warm-up).
    Parity: TA-Lib ``WCLPRICE`` / pandas-ta ``wcp``.
    """

    spec = IndicatorSpec(
        name="wcp",
        category="price_transform",
        aliases=("WCLPRICE", "Weighted Close"),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("wcp",),
        talib_compatible=True,
        references=("TA-Lib WCLPRICE", "pandas-ta wcp"),
        doc="ref/ta_docs/price_transform/price_transforms.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return wcp(df)
