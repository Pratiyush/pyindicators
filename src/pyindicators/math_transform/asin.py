"""ASIN — element-wise arcsine of ``close`` (math transform).

A vectorised wrapper over the inverse-sine: ``asin(x)`` returns the angle in radians whose
sine is ``x``. It is defined only on the domain ``[-1, 1]``; anywhere outside that the result
is undefined and emitted as NaN (we do NOT clamp — clamping would fabricate a value TA-Lib
does not produce). Because raw prices almost always sit outside ``[-1, 1]``, ASIN is meant for
already-normalised inputs (e.g. a correlation/oscillator in ``[-1, 1]``). See
``ref/ta_docs/math_transform/math_transform.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def asin(close: pd.Series) -> pd.Series:
    """Element-wise arcsine of ``close``, in radians and bounded ``[-pi/2, pi/2]``.

    Domain-guarded: values with ``|close| > 1`` are undefined and returned as NaN (NumPy's
    ``arcsin`` already does this); pre-existing warm-up NaNs propagate unchanged.
    """
    with np.errstate(invalid="ignore"):
        out = np.arcsin(close.to_numpy(dtype="float64"))
    return pd.Series(out, index=close.index)


@INDICATORS.register
class ASIN(Indicator):
    """Arcsine (ASIN).

    What: per-bar inverse sine of ``close`` (radians), the functional inverse of ``sin``.
    Best settings: none (stateless per-bar transform); feed inputs already scaled to [-1, 1].
    Edge cases: ``|close| > 1`` is out of domain -> NaN; ``+/-1`` map to ``+/-pi/2``; 0 -> 0.
    Parity: TA-Lib ``ASIN`` (identical to ``numpy.arcsin``; out-of-domain -> NaN).
    """

    spec = IndicatorSpec(
        name="asin",
        category="math_transform",
        aliases=("Arcsine", "ASIN"),
        inputs=(CLOSE,),
        outputs=("asin",),
        bounds={"asin": (-np.pi / 2.0, np.pi / 2.0)},
        talib_compatible=True,
        references=("TA-Lib ASIN", "numpy.arcsin"),
        doc="ref/ta_docs/math_transform/math_transform.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return asin(df[CLOSE])
