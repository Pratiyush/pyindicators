"""BOP — Balance of Power: ``(close - open) / (high - low)`` (momentum)."""

from __future__ import annotations

import pandas as pd

from pyindicators.core import (
    CLOSE,
    HIGH,
    INDICATORS,
    LOW,
    OPEN,
    Indicator,
    IndicatorSpec,
    safe_divide,
)


def bop(df: pd.DataFrame) -> pd.Series:
    """Balance of Power = (close - open) / (high - low), per bar."""
    return safe_divide(df[CLOSE] - df[OPEN], df[HIGH] - df[LOW])  # H==L -> NaN


@INDICATORS.register
class BOP(Indicator):
    """Balance of Power.

    What: where the close finishes within the bar relative to the open ([-1, 1]).
    Best settings: per-bar (no smoothing).
    Edge cases: High==Low (zero range) -> guarded to NaN.
    Parity: TA-Lib ``BOP`` / pandas-ta ``bop``.
    """

    spec = IndicatorSpec(
        name="bop",
        category="momentum",
        aliases=("Balance of Power",),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("bop",),
        bounds={"bop": (-1.0, 1.0)},
        talib_compatible=True,
        references=("TA-Lib BOP", "pandas-ta bop"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return bop(df)
