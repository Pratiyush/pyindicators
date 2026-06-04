"""TAN — element-wise tangent of ``close`` (math transform).

A per-bar pointwise transform: ``tan(close)`` with ``close`` taken in radians, mirroring
TA-Lib ``TAN`` (a thin wrapper over the C library ``tan``, i.e. NumPy's ``np.tan``). Pure
function of the current bar, so there is no warm-up and no look-ahead. Unbounded: tan
diverges toward +/-inf near odd multiples of pi/2. See ``ref/ta_docs/math_transform``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def tan(close: pd.Series) -> pd.Series:
    """Element-wise tangent of ``close`` (radians), matching ``np.tan`` / TA-Lib ``TAN``.

    A pure pointwise map with no smoothing, so an all-NaN input stays NaN and every finite
    input maps to ``tan(x)``. Unbounded near odd multiples of pi/2 (values blow up but stay
    finite at float64 resolution since exact pi/2 is not representable).
    """
    return pd.Series(np.tan(close.to_numpy(dtype="float64")), index=close.index)


@INDICATORS.register
class Tan(Indicator):
    """Tangent (math transform).

    What: the element-wise tangent of ``close`` (interpreted in radians).
    Best settings: none (per-bar transform, no parameters).
    Edge cases: no warm-up; unbounded (diverges near odd multiples of pi/2); NaN -> NaN.
    Parity: TA-Lib ``TAN`` (== ``np.tan``); exact closed-form oracle.
    """

    spec = IndicatorSpec(
        name="tan",
        category="math_transform",
        aliases=("TAN", "Tangent"),
        inputs=(CLOSE,),
        outputs=("tan",),
        talib_compatible=True,
        references=("TA-Lib TAN", "numpy tan"),
        doc="ref/ta_docs/math_transform/math_transforms.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return tan(df[CLOSE])
