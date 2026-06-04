"""FLOOR — element-wise floor of ``close`` (math transform).

The largest integer ``<= close`` for each bar (``floor(1.2) == 1``, ``floor(-1.2) == -2``).
A pure per-bar vectorised transform with no window, no parameters, and no warm-up; ``NaN``
inputs stay ``NaN`` (``numpy.floor`` propagates them, so no fabricated values). Mirrors
TA-Lib ``FLOOR``. See ``ref/ta_docs/math_transform/math_transforms.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def floor(close: pd.Series) -> pd.Series:
    """Element-wise floor: greatest integer ``<= close`` per bar.

    ``numpy.floor`` rounds toward negative infinity (``-2.7 -> -3``) and preserves ``NaN``
    and ``+/-inf``, so warm-up/missing values pass through untouched.
    """
    return pd.Series(np.floor(close.to_numpy(dtype="float64")), index=close.index)


@INDICATORS.register
class Floor(Indicator):
    """Floor (math transform).

    What: the largest integer not greater than each ``close`` value (round toward -inf).
    Best settings: none (stateless per-bar transform, no parameters).
    Edge cases: integers map to themselves; ``NaN`` -> ``NaN``; ``-2.7`` -> ``-3``.
    Parity: TA-Lib ``FLOOR`` (identical to ``numpy.floor`` element-wise; exact, atol 0).
    """

    spec = IndicatorSpec(
        name="floor",
        category="math_transform",
        aliases=("FLOOR",),
        inputs=(CLOSE,),
        outputs=("floor",),
        talib_compatible=True,
        references=("TA-Lib FLOOR", "numpy.floor"),
        doc="ref/ta_docs/math_transform/math_transforms.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return floor(df[CLOSE])
