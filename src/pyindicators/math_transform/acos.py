"""ACOS — element-wise arccosine of ``close`` (math transform).

A pure per-bar vectorised transform: ``acos(close)`` mapping each input onto its angle in
radians. ``arccos`` is only real-valued on the closed interval ``[-1, 1]``, so inputs outside
that domain are guarded to NaN (mirroring TA-Lib ``ACOS``, which returns NaN there) rather than
fabricating a complex/forced value. The output is bounded in ``[0, pi]`` (``acos(1)=0``,
``acos(-1)=pi``, ``acos(0)=pi/2``). Wraps ``numpy.arccos`` — NumPy is the project's numeric
core, so there is no base-math helper to compose here; this *is* the primitive. See
``ref/ta_docs/math_transform/math_transform.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def acos(close: pd.Series) -> pd.Series:
    """Element-wise arccosine of ``close`` in radians, bounded ``[0, pi]``.

    No look-ahead and no warm-up: every bar maps to exactly its own value. The ``errstate``
    guard only silences NumPy's "invalid value" warning — inputs with ``|close| > 1`` still
    resolve to NaN, which is the intended (undefined-domain) result and matches TA-Lib ``ACOS``.
    NaNs already present propagate as NaN.
    """
    with np.errstate(invalid="ignore"):
        result = np.arccos(close.to_numpy(dtype="float64"))
    return pd.Series(result, index=close.index)


@INDICATORS.register
class ACOS(Indicator):
    """Arccosine (ACOS).

    What: the element-wise inverse-cosine of ``close`` (radians), a per-bar math transform —
    typically a building block rather than a standalone signal.
    Best settings: none (stateless, parameter-free element-wise op).
    Edge cases: ``|close| > 1`` -> NaN (real arccos is undefined there); ``acos(1)=0``,
        ``acos(-1)=pi``, ``acos(0)=pi/2``; NaN propagates. No window, so no warm-up NaNs.
    Parity: TA-Lib ``ACOS`` (identical to ``numpy.arccos`` with the same ``[-1, 1]``
        domain guard). Raw OHLCV closes (>> 1) are out of domain, so parity is exercised on a
        close rescaled into ``[-1, 1]``; on raw prices both sides agree by being all-NaN.
    """

    spec = IndicatorSpec(
        name="acos",
        category="math_transform",
        aliases=("Arccosine", "ACOS"),
        inputs=(CLOSE,),
        outputs=("acos",),
        bounds={"acos": (0.0, np.pi)},
        talib_compatible=True,
        references=("TA-Lib ACOS", "numpy arccos"),
        doc="ref/ta_docs/math_transform/math_transform.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return acos(df[CLOSE])
