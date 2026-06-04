"""ADD — element-wise sum of two series (math transform).

A pointwise binary vector-math op (no window, no state, no smoothing): ``high + low`` computed
per bar. This is the math-transform analogue of TA-Lib ``ADD(high, low)`` — the literal sum of
the two input series. NaN propagates naturally (``NaN + x == NaN``), matching TA-Lib, so there
is nothing to seed or guard. Wraps plain pandas/NumPy addition (this *is* the primitive — there
is no base-math helper to compose). See ``ref/ta_docs/math_transform/math_transform.md``.
"""

from __future__ import annotations

import pandas as pd

from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def add(high: pd.Series, low: pd.Series) -> pd.Series:
    """Element-wise sum ``high + low``, aligned on the index and returned as float64.

    No look-ahead and no warm-up: every bar maps to exactly its own two inputs. NaN in either
    operand yields NaN at that bar (undefined sum, not a fabricated value) — identical to
    TA-Lib ``ADD``.
    """
    result = high.to_numpy(dtype="float64") + low.to_numpy(dtype="float64")
    return pd.Series(result, index=high.index)


@INDICATORS.register
class Add(Indicator):
    """Vector Arithmetic Add (math transform).

    What: pointwise ``high + low`` — the literal element-wise sum of the two input series, a
    building block (e.g. the numerator of a midpoint) rather than a standalone signal.
    Best settings: none (parameter-free binary element-wise op).
    Edge cases: NaN in either input -> NaN at that bar; no window, so no warm-up NaNs.
    Parity: TA-Lib ``ADD`` (identical to element-wise NumPy addition with the same NaN
    propagation).
    """

    spec = IndicatorSpec(
        name="add",
        category="math_transform",
        aliases=("Vector Arithmetic Add", "ADD"),
        inputs=(HIGH, LOW),
        outputs=("add",),
        talib_compatible=True,
        references=("TA-Lib ADD", "numpy.add"),
        doc="ref/ta_docs/math_transform/math_transform.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return add(df[HIGH], df[LOW])
