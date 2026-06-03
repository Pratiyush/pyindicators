"""True Range (base / volatility primitive).

The gap-aware measure of one bar's movement: ``max(H-L, |H-prevC|, |L-prevC|)``. Input to
ATR, NATR, Supertrend, Keltner, Chandelier, Ultimate Oscillator, Vortex. First bar has no
prior close, so it falls back to ``H-L`` (matching pandas-ta/finta; TA-Lib leaves bar 0
undefined — a documented divergence). See ``ref/ta_docs/base/TrueRange.md``.
"""

from __future__ import annotations

import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def true_range(df: pd.DataFrame) -> pd.Series:
    """Wilder's True Range. First bar falls back to ``high - low`` (no previous close)."""
    high, low, close = df[HIGH], df[LOW], df[CLOSE]
    prev_close = close.shift(1)
    tr = pd.concat(
        [(high - low), (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    tr.iloc[:1] = (high - low).iloc[:1]  # no prior close on the first bar
    return tr


@INDICATORS.register
class TrueRange(Indicator):
    """True Range.

    What: the greatest of the bar range and the two gaps to the prior close (gap-aware).
    Best settings: none (per-bar); a period is applied later by ATR.
    Edge cases: first bar = H-L; a flat no-gap bar = 0 (legitimate; ATR handles it).
    Parity: TA-Lib ``TRANGE`` (from bar 1) / pandas-ta ``true_range``.
    """

    spec = IndicatorSpec(
        name="true_range",
        category="base",
        aliases=("TR", "TRANGE"),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("true_range",),
        talib_compatible=True,
        references=("TA-Lib TRANGE", "pandas-ta true_range", "tulip tr"),
        doc="ref/ta_docs/base/TrueRange.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return true_range(df)
