"""sinh / SINH — element-wise hyperbolic sine of close (math transform).

A pure per-bar trigonometric transform: ``sinh(x) = (e**x - e**-x) / 2``, applied to
``close``. Defined and finite for every real input (it is *not* one of the domain-guarded
transforms like ``ln``/``sqrt``/``asin``); it is unbounded and grows exponentially, so for
large inputs it legitimately overflows to ``+/-inf``. No warm-up, no parameters. See
``ref/ta_docs/math_transform/math_transforms.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def sinh(close: pd.Series) -> pd.Series:
    """Element-wise hyperbolic sine of ``close``.

    Defined for all reals, so there is no domain guard; NaNs propagate and very large
    magnitudes overflow to ``+/-inf`` (matching TA-Lib, which wraps the C ``sinh``).
    """
    return pd.Series(np.sinh(close.to_numpy(dtype="float64")), index=close.index)


@INDICATORS.register
class Sinh(Indicator):
    """Hyperbolic Sine (sinh).

    What: per-bar ``sinh(close)`` — an odd, exponentially-growing transform of price.
    Best settings: none (stateless per-bar transform; no length/params).
    Edge cases: defined everywhere (no NaN domain); huge inputs overflow to +/-inf; NaN -> NaN.
    Parity: TA-Lib ``SINH`` (exact, vectorised ``numpy.sinh``).
    """

    spec = IndicatorSpec(
        name="sinh",
        category="math_transform",
        aliases=("SINH", "Hyperbolic Sine"),
        inputs=(CLOSE,),
        outputs=("sinh",),
        talib_compatible=True,
        references=("TA-Lib SINH", "numpy.sinh"),
        doc="ref/ta_docs/math_transform/math_transforms.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return sinh(df[CLOSE])
