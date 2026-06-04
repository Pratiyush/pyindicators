"""tanh — element-wise hyperbolic tangent of ``close`` (math transform).

A pure per-bar mapping ``y = tanh(close)`` with no window and no parameters. Squashes the
input onto the open interval ``(-1, 1)`` (saturating to +/-1 in the limit), so it is a natural
bounded transform but only meaningful on already-normalised series (z-scores, oscillator
output) rather than raw price. NaN propagates unchanged; +/-inf map to +/-1. TA-Lib's
``TANH`` has a zero lookback, so the output is index-aligned with the input (no warm-up
shift). See ``ref/ta_docs/math_transform/math_transform.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def tanh(close: pd.Series) -> pd.Series:
    """Element-wise hyperbolic tangent of ``close``, bounded (-1, 1)."""
    return pd.Series(np.tanh(close.to_numpy(dtype="float64")), index=close.index)


@INDICATORS.register
class Tanh(Indicator):
    """Hyperbolic Tangent (math transform).

    What: per-bar ``tanh(close)``; a smooth sigmoid squashing the input onto (-1, 1).
    Best settings: none (parameter-free element-wise map); apply to normalised inputs.
    Edge cases: NaN -> NaN; +/-inf -> +/-1; zero lookback so no warm-up / no shift.
    Parity: TA-Lib ``TANH`` (== ``numpy.tanh``, exact).
    """

    spec = IndicatorSpec(
        name="tanh",
        category="math_transform",
        aliases=("TANH", "Hyperbolic Tangent"),
        inputs=(CLOSE,),
        outputs=("tanh",),
        bounds={"tanh": (-1.0, 1.0)},
        talib_compatible=True,
        references=("TA-Lib TANH", "numpy tanh"),
        doc="ref/ta_docs/math_transform/math_transform.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return tanh(df[CLOSE])
