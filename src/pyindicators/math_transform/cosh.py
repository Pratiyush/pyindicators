"""cosh — element-wise hyperbolic cosine of ``close`` (math transform).

A vectorised wrapper over ``numpy.cosh`` exposed as a first-class indicator so it can be
composed/screened uniformly. ``cosh`` is defined and finite on the whole real line, so there
is no domain guard and no warm-up; it is symmetric (``cosh(-x) == cosh(x)``) and >= 1.
See ``ref/ta_docs/math_transform/math_transform.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def cosh(close: pd.Series) -> pd.Series:
    """Hyperbolic cosine of ``close``, element-wise: ``(e**x + e**-x) / 2``.

    Pure per-bar transform: no look-ahead, no smoothing, no warm-up. Defined for every
    real input (NaNs propagate as NaN); the result is always >= 1.
    """
    return pd.Series(np.cosh(close.to_numpy(dtype="float64")), index=close.index)


@INDICATORS.register
class Cosh(Indicator):
    """Hyperbolic Cosine (cosh).

    What: element-wise ``cosh(close)`` — a math transform, not a smoother.
    Best settings: none (stateless per-bar transform).
    Edge cases: none — defined on all reals; NaNs propagate; output is always >= 1.
    Parity: TA-Lib ``COSH`` (== ``numpy.cosh``), exact to floating point.
    """

    spec = IndicatorSpec(
        name="cosh",
        category="math_transform",
        aliases=("COSH", "Hyperbolic Cosine"),
        inputs=(CLOSE,),
        outputs=("cosh",),
        talib_compatible=True,
        references=("TA-Lib COSH", "numpy.cosh"),
        doc="ref/ta_docs/math_transform/math_transform.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return cosh(df[CLOSE])
