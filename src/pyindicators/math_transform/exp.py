"""EXP — element-wise exponential ``e**close`` (math transform).

A pure per-bar vector transform: maps each ``close`` to ``e ** close`` with no window,
no state, and no look-ahead. Mirrors TA-Lib ``EXP`` exactly (a thin wrapper over
``numpy.exp``); NaNs in the input propagate to NaN. ``exp`` is unbounded above and strictly
positive below, so it carries no ``bounds``. See ``ref/ta_docs/math_transform/EXP.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def exp(close: pd.Series) -> pd.Series:
    """Element-wise natural exponential ``e ** close``.

    Exact and warm-up-free: each output depends only on its own bar. NaNs propagate
    (``exp(NaN) == NaN``); very large inputs overflow to ``+inf`` exactly as ``numpy.exp``
    (hence TA-Lib ``EXP``) does, so no domain guard is needed.
    """
    return pd.Series(np.exp(close.to_numpy(dtype="float64")), index=close.index)


@INDICATORS.register
class EXP(Indicator):
    """Vector Arithmetic Exp.

    What: the element-wise natural exponential of ``close`` (``e ** close``).
    Best settings: none (stateless per-bar transform; no parameters).
    Edge cases: NaN -> NaN; large positive close -> +inf (IEEE overflow, like numpy/TA-Lib).
    Parity: TA-Lib ``EXP`` (identical to ``numpy.exp``, element-wise, NaN-propagating).
    """

    spec = IndicatorSpec(
        name="exp",
        category="math_transform",
        aliases=("Vector Arithmetic Exp", "EXP"),
        inputs=(CLOSE,),
        outputs=("exp",),
        talib_compatible=True,
        references=("TA-Lib EXP", "numpy.exp"),
        doc="ref/ta_docs/math_transform/EXP.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return exp(df[CLOSE])
