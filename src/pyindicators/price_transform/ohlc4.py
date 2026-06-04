"""ohlc4 / AVGPRICE — average price ``(open + high + low + close) / 4`` (price transform)."""

from __future__ import annotations

import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec


def ohlc4(df: pd.DataFrame) -> pd.Series:
    """Average price: (open + high + low + close) / 4."""
    return (df[OPEN] + df[HIGH] + df[LOW] + df[CLOSE]) / 4.0


@INDICATORS.register
class OHLC4(Indicator):
    """Average Price (ohlc4).

    What: the mean of the four OHLC prices; the smoothest single-bar price proxy.
    Best settings: none (per-bar transform).
    Edge cases: none (exact, no warm-up).
    Parity: TA-Lib ``AVGPRICE`` / pandas-ta ``ohlc4``.
    """

    spec = IndicatorSpec(
        name="ohlc4",
        category="price_transform",
        aliases=("AVGPRICE", "Average Price"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("ohlc4",),
        talib_compatible=True,
        references=("TA-Lib AVGPRICE", "pandas-ta ohlc4"),
        doc="ref/ta_docs/price_transform/price_transforms.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return ohlc4(df)
