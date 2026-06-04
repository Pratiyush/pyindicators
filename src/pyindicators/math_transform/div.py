"""DIV — element-wise division of two series, ``high / low`` (math transform).

A pointwise binary vector-math op (no window, no state): each bar maps to ``high / low`` for
that bar only. TA-Lib ``DIV`` is the raw quotient and emits ``inf`` when the denominator is 0;
this implementation instead guards division-by-zero to NaN via ``safe_divide`` (the library's
CONVENTIONS.md treatment of the single most common indicator hazard) rather than fabricating an
infinity. On genuine OHLCV ``low`` is strictly positive, so the guard never fires and the result
is identical to TA-Lib. ``div(NaN, x) == div(x, NaN) == NaN`` falls out naturally. Composes
``core.safe_divide``. See ``ref/ta_docs/math_transform/math_transform.md``.
"""

from __future__ import annotations

import pandas as pd

from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec, safe_divide


def div(high: pd.Series, low: pd.Series) -> pd.Series:
    """Element-wise ``high / low``; NaN where ``low == 0`` (or either input is already NaN).

    No look-ahead and no warm-up: every bar maps to exactly its own quotient. The zero
    denominator is guarded to NaN (vs TA-Lib's ``inf``) per the library's safe-division policy;
    on real OHLCV ``low`` is positive, so this never diverges from TA-Lib ``DIV`` in practice.
    """
    return safe_divide(high.astype("float64"), low.astype("float64"))


@INDICATORS.register
class Div(Indicator):
    """Vector Arithmetic Div (math transform).

    What: pointwise ``high / low`` — the raw per-bar ratio of the two series (a building block
    rather than a standalone signal).
    Best settings: none (parameter-free binary element-wise op).
    Edge cases: ``low == 0`` -> NaN (guarded vs TA-Lib's ``inf``); NaN in either input
    propagates. No window, so no warm-up NaNs.
    Parity: TA-Lib ``DIV`` (identical to ``high / low``; differs only on the zero-denominator
    domain, which never occurs on real OHLCV where ``low`` is strictly positive).
    """

    spec = IndicatorSpec(
        name="div",
        category="math_transform",
        aliases=("Vector Arithmetic Div", "DIV"),
        inputs=(HIGH, LOW),
        outputs=("div",),
        talib_compatible=True,
        references=("TA-Lib DIV",),
        doc="ref/ta_docs/math_transform/math_transform.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return div(df[HIGH], df[LOW])
