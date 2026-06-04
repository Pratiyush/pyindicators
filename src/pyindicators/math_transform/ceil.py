"""ceil — element-wise ceiling of ``close`` (math transform).

The smallest integer-valued float ``>= close`` for each bar, i.e. ``numpy.ceil`` applied
pointwise. A pure, memory-less vector transform (no window, no smoothing, no state): the
value at bar ``i`` depends only on ``close[i]``. NaNs propagate unchanged. See
``ref/ta_docs/math_transform/math_transforms.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def ceil(close: pd.Series) -> pd.Series:
    """Element-wise ceiling of ``close`` (smallest integer float ``>=`` each value).

    Pure pointwise transform: order-independent, no warm-up. NaN in -> NaN out; ``+/-inf``
    map to themselves. Unbounded (the codomain is all integer-valued floats), so the spec
    declares no bounds.
    """
    return pd.Series(np.ceil(close.to_numpy(dtype="float64")), index=close.index)


@INDICATORS.register
class Ceil(Indicator):
    """Ceiling.

    What: element-wise ceiling of ``close`` (smallest integer-valued float ``>=`` price).
    Best settings: none — parameter-free pointwise transform.
    Edge cases: NaN -> NaN; integers unchanged; ceil of a value in ``(-1, 0)`` is ``-0.0``.
    Parity: TA-Lib ``CEIL`` (``numpy.ceil``; lookback 0, exact element-wise match).
    """

    spec = IndicatorSpec(
        name="ceil",
        category="math_transform",
        aliases=("CEIL", "Vector Ceil"),
        inputs=(CLOSE,),
        outputs=("ceil",),
        talib_compatible=True,
        references=("TA-Lib CEIL", "numpy.ceil"),
        doc="ref/ta_docs/math_transform/math_transforms.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return ceil(df[CLOSE])
