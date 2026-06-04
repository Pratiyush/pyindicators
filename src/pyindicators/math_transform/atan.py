"""ATAN — element-wise arctangent of ``close`` (math transform).

A pure per-bar vectorised transform: ``atan(close)`` mapping each price onto its angle in
radians. ``arctan`` is defined for every real input (no domain guard needed) and is bounded
in the open interval ``(-pi/2, pi/2)``, which it approaches asymptotically as |close| grows.
Wraps ``numpy.arctan``; see ``ref/ta_docs/math_transform/math_transforms.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def atan(close: pd.Series) -> pd.Series:
    """Element-wise arctangent of ``close`` in radians, bounded ``(-pi/2, pi/2)``.

    Defined for all reals (no warm-up, no domain mask). NaNs already present propagate.
    """
    return pd.Series(np.arctan(close.to_numpy(dtype="float64")), index=close.index)


@INDICATORS.register
class ATAN(Indicator):
    """Arctangent (ATAN).

    What: the element-wise inverse-tangent of ``close`` (radians), a per-bar math transform.
    Best settings: none (stateless, no parameters).
    Edge cases: none — ``arctan`` is total over the reals; constant input -> constant output;
        ``+/-inf`` maps to ``+/-pi/2`` and NaN propagates as NaN.
    Parity: TA-Lib ``ATAN`` (== ``numpy.arctan``).
    """

    spec = IndicatorSpec(
        name="atan",
        category="math_transform",
        aliases=("Arctangent", "ATAN"),
        inputs=(CLOSE,),
        outputs=("atan",),
        bounds={"atan": (-np.pi / 2.0, np.pi / 2.0)},
        talib_compatible=True,
        references=("TA-Lib ATAN", "numpy arctan"),
        doc="ref/ta_docs/math_transform/math_transforms.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return atan(df[CLOSE])
