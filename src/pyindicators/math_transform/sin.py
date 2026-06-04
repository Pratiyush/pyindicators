"""SIN — element-wise trigonometric sine of ``close`` (math transform).

A pure per-bar vector transform: ``sin(close)`` computed independently on every bar, with no
window, no warm-up, and no look-ahead. The closing price is treated as the angle in radians
(TA-Lib's convention for its Math Transform family). NaN inputs propagate to NaN outputs.
Bounded to ``[-1, 1]`` by the sine function itself. See ``ref/ta_docs/math_transform``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def sin(close: pd.Series) -> pd.Series:
    """Element-wise sine of ``close`` (angle in radians), bounded ``[-1, 1]``.

    Pure transform: ``out[i] = sin(close[i])``. The full real line is in the domain, so there
    is nothing to guard; existing NaNs simply propagate (``np.sin(NaN) == NaN``).
    """
    return pd.Series(np.sin(close.to_numpy(dtype="float64")), index=close.index)


@INDICATORS.register
class SIN(Indicator):
    """Vector Trigonometric Sin.

    What: element-wise ``sin(close)`` with ``close`` interpreted as an angle in radians.
    Best settings: none (stateless per-bar transform; rarely used directly on raw prices).
    Edge cases: domain is all reals -> no guarding; NaN in -> NaN out; output is in [-1, 1].
    Parity: TA-Lib ``SIN`` (identical to ``numpy.sin``, element-wise).
    """

    spec = IndicatorSpec(
        name="sin",
        category="math_transform",
        aliases=("Vector Trigonometric Sin", "SIN"),
        inputs=(CLOSE,),
        outputs=("sin",),
        bounds={"sin": (-1.0, 1.0)},
        talib_compatible=True,
        references=("TA-Lib SIN", "numpy.sin"),
        doc="ref/ta_docs/math_transform/math_transforms.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return sin(df[CLOSE])
