"""sub — element-wise subtraction of two series, ``high - low`` (math transform).

The pointwise difference of the high and low series, i.e. ``numpy``-style binary subtraction
applied bar-by-bar. A pure, memory-less vector transform (no window, no smoothing, no state):
the value at bar ``i`` depends only on ``high[i]`` and ``low[i]``. With (high, low) inputs this
is simply the bar's range. NaNs propagate unchanged. ``+/-inf`` follow IEEE arithmetic
(``inf - inf -> NaN``). No division is involved, so ``safe_divide`` does not apply. See
``ref/ta_docs/math_transform/math_transforms.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict

from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def sub(high: pd.Series, low: pd.Series) -> pd.Series:
    """Element-wise ``high - low`` (the per-bar difference of the two series).

    Pure pointwise transform: order-independent, no warm-up. NaN in either operand -> NaN out;
    ``inf - inf`` -> NaN by IEEE rules. Unbounded codomain, so the spec declares no bounds.
    """
    diff = high.to_numpy(dtype="float64") - low.to_numpy(dtype="float64")
    return pd.Series(diff, index=high.index)


@INDICATORS.register
class Sub(Indicator):
    """Vector Arithmetic Subtraction.

    What: element-wise ``high - low`` — with (high, low) inputs this is the bar's range.
    Best settings: none — parameter-free pointwise transform.
    Edge cases: NaN in either input -> NaN; ``inf - inf`` -> NaN; lookback 0 (no warm-up).
    Parity: TA-Lib ``SUB`` (``real0 - real1``; exact element-wise match, no seeding).
    """

    spec = IndicatorSpec(
        name="sub",
        category="math_transform",
        aliases=("SUB", "Vector Arithmetic Subtraction"),
        inputs=(HIGH, LOW),
        outputs=("sub",),
        talib_compatible=True,
        references=("TA-Lib SUB",),
        doc="ref/ta_docs/math_transform/math_transforms.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return sub(df[HIGH], df[LOW])
