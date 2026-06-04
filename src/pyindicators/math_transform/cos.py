"""COS — element-wise cosine of close (math transform).

A bar-by-bar pointwise application of ``numpy.cos`` to ``close``. There is no window, no
state, and no warm-up; ``cos(NaN)`` propagates as NaN. The mathematical range of cosine is
[-1, 1], but TA-Lib's COS declares no output bounds (it is a raw transform, not a bounded
oscillator), so we follow that and leave ``bounds`` empty. See
``ref/ta_docs/math_transform/math_transforms.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def cos(close: pd.Series) -> pd.Series:
    """Element-wise cosine of ``close`` (radians); NaNs propagate."""
    return np.cos(close)


@INDICATORS.register
class COS(Indicator):
    """Vector Trigonometric Cos.

    What: the cosine of each close value, treated as an angle in radians (pointwise).
    Best settings: none (per-bar transform; no length parameter).
    Edge cases: no warm-up; NaN in -> NaN out; output is mathematically in [-1, 1] but
    declared unbounded to mirror TA-Lib's raw transform.
    Parity: TA-Lib ``COS`` (identically ``numpy.cos``).
    """

    spec = IndicatorSpec(
        name="cos",
        category="math_transform",
        aliases=("Vector Trigonometric Cos", "COS"),
        inputs=(CLOSE,),
        outputs=("cos",),
        talib_compatible=True,
        references=("TA-Lib COS", "numpy.cos"),
        doc="ref/ta_docs/math_transform/math_transforms.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return cos(df[CLOSE])
