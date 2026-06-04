"""SQRT — element-wise square root of close (math transform).

A pointwise vector-math op (no window, no state): ``sqrt(close)`` computed per bar. The square
root is only real-valued on the non-negative reals, so the negative domain is guarded to NaN
(mirroring TA-Lib, which returns NaN there) rather than fabricating a complex/forced value.
``sqrt(0) == 0`` and ``sqrt(NaN) == NaN`` fall out naturally. Wraps ``numpy.sqrt`` (NumPy is
already the project's numeric core, so there is no base-math helper to compose here — this *is*
the primitive). See ``ref/ta_docs/math_transform/math_transform.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def sqrt(close: pd.Series) -> pd.Series:
    """Element-wise square root of ``close``; NaN where the input is negative (or already NaN).

    No look-ahead and no warm-up: every bar maps to exactly its own value. The ``errstate``
    guard only silences NumPy's "invalid value" warning — negatives still resolve to NaN, which
    is the intended (undefined-domain) result and matches TA-Lib ``SQRT``.
    """
    with np.errstate(invalid="ignore"):
        result = np.sqrt(close.to_numpy(dtype="float64"))
    return pd.Series(result, index=close.index)


@INDICATORS.register
class Sqrt(Indicator):
    """Square Root (math transform).

    What: pointwise ``sqrt(close)`` — a variance-stabilising / scale-compressing transform,
    often a building block rather than a standalone signal.
    Best settings: none (parameter-free element-wise op).
    Edge cases: negative input -> NaN (real sqrt is undefined there); ``sqrt(0)=0``;
    NaN propagates. No window, so no warm-up NaNs.
    Parity: TA-Lib ``SQRT`` (identical to ``numpy.sqrt`` with the same negative-domain guard).
    """

    spec = IndicatorSpec(
        name="sqrt",
        category="math_transform",
        aliases=("Square Root", "SQRT"),
        inputs=(CLOSE,),
        outputs=("sqrt",),
        talib_compatible=True,
        references=("TA-Lib SQRT", "numpy.sqrt"),
        doc="ref/ta_docs/math_transform/math_transform.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return sqrt(df[CLOSE])
