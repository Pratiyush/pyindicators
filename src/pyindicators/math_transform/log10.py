"""log10 / LOG10 — element-wise base-10 logarithm of close (math transform).

Maps each ``close`` to ``log10(close)``. Logarithms compress multiplicative price
scales into additive ones, so equal *percentage* moves become equal *vertical* moves —
the basis for log-scale charts and log-return work. The base-10 log is undefined for
non-positive inputs, so the domain is guarded to NaN there (CONVENTIONS.md: never
fabricate a value where the math is undefined). See ``ref/ta_docs/math_transform``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def log10(close: pd.Series) -> pd.Series:
    """Element-wise ``log10(close)``; NaN wherever ``close <= 0`` (out of domain).

    Existing NaNs propagate as NaN. On the positive domain this is exactly TA-Lib's
    ``LOG10`` / ``numpy.log10``; the only difference is that non-positive inputs become
    NaN here instead of ``-inf`` (at zero) or ``nan`` (at negatives).
    """
    values = close.to_numpy(dtype="float64")
    positive = values > 0.0
    out = np.full(values.shape, np.nan, dtype="float64")
    with np.errstate(divide="ignore", invalid="ignore"):
        out[positive] = np.log10(values[positive])
    return pd.Series(out, index=close.index)


@INDICATORS.register
class LOG10(Indicator):
    """Base-10 Logarithm (log10).

    What: per-bar ``log10(close)`` — a static math transform with no look-back/look-ahead.
    Best settings: none (element-wise; no parameters).
    Edge cases: ``close <= 0`` is out of domain -> NaN (vs TA-Lib's -inf at 0 / nan at <0);
        pre-existing NaNs propagate.
    Parity: TA-Lib ``LOG10`` (== ``numpy.log10``) on the positive domain; finite-masked,
        so the -inf/nan edge encodings are excluded from the comparison.
    """

    spec = IndicatorSpec(
        name="log10",
        category="math_transform",
        aliases=("LOG10", "Base-10 Logarithm"),
        inputs=(CLOSE,),
        outputs=("log10",),
        talib_compatible=True,
        references=("TA-Lib LOG10", "numpy.log10"),
        doc="ref/ta_docs/math_transform/math_transform.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return log10(df[CLOSE])
