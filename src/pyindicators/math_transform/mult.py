"""MULT — element-wise product of two series (math transform).

A pointwise binary vector-math op (no window, no state, no division): ``high * low`` computed
per bar. This is the two-input arithmetic primitive from TA-Lib's Math Operators group
(``MULT(real0, real1)``); here it is wired to the high and low series. There is nothing to
guard — multiplication is total on the reals — so the only edge behaviour is NaN propagation
(NaN in either input -> NaN), which falls out of NumPy naturally and matches TA-Lib. Wraps a
plain ``*`` on the float64 arrays (NumPy is already the project's numeric core, so there is no
base-math helper to compose — this *is* the primitive). See
``ref/ta_docs/math_transform/math_transform.md``.
"""

from __future__ import annotations

import pandas as pd

from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def mult(high: pd.Series, low: pd.Series) -> pd.Series:
    """Element-wise product ``high * low``, aligned on ``high``'s index.

    No look-ahead and no warm-up: every bar maps to exactly its own two inputs. NaN in either
    operand yields NaN at that bar (TA-Lib ``MULT`` behaviour); no division, so nothing to
    guard against. Both operands are coerced to float64 so the output dtype is stable.
    """
    h = high.to_numpy(dtype="float64")
    low_a = low.to_numpy(dtype="float64")
    return pd.Series(h * low_a, index=high.index)


@INDICATORS.register
class MULT(Indicator):
    """Vector Arithmetic Mult (math transform).

    What: pointwise ``high * low`` — the two-input multiplication primitive (a building block,
    e.g. price*volume style products, rather than a standalone signal).
    Best settings: none (parameter-free element-wise op).
    Edge cases: NaN in either input -> NaN; no window, so no warm-up NaNs.
    Parity: TA-Lib ``MULT`` (identical to an element-wise ``*`` with the same NaN behaviour).
    """

    spec = IndicatorSpec(
        name="mult",
        category="math_transform",
        aliases=("Vector Arithmetic Mult", "MULT"),
        inputs=(HIGH, LOW),
        outputs=("mult",),
        talib_compatible=True,
        references=("TA-Lib MULT", "numpy multiply"),
        doc="ref/ta_docs/math_transform/math_transform.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return mult(df[HIGH], df[LOW])
