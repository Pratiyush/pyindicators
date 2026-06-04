"""LN — element-wise natural logarithm of close (math transform).

Per-bar ``ln(close)``, the vectorised math primitive TA-Lib exposes as ``LN``. The natural
log is only defined for strictly positive inputs, so the domain is guarded: ``close <= 0``
maps to NaN (undefined) rather than fabricating a value. See ``ref/ta_docs/math_transform``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def ln(close: pd.Series) -> pd.Series:
    """Natural logarithm of ``close`` element-wise, NaN where ``close <= 0`` (out of domain).

    ln(x) is defined only for x > 0. We guard the whole non-positive half-line to NaN: x < 0
    has no real log, and x == 0 is the -inf singularity (TA-Lib returns -inf there — see the
    Parity note). Pre-existing warm-up NaNs propagate as NaN.
    """
    values = close.to_numpy(dtype="float64")
    out = np.full(values.shape, np.nan, dtype="float64")
    positive = values > 0.0
    with np.errstate(divide="ignore", invalid="ignore"):
        out[positive] = np.log(values[positive])
    return pd.Series(out, index=close.index)


@INDICATORS.register
class LN(Indicator):
    """Natural Logarithm (ln).

    What: per-bar natural log of close; a math primitive (log returns, log-scale charts).
    Best settings: none (stateless element-wise transform, no warm-up).
    Edge cases: close <= 0 is out of domain -> guarded to NaN (TA-Lib emits -inf at 0).
    Parity: TA-Lib ``LN`` on positive prices; we map close == 0 to NaN where TA-Lib gives
    -inf (a domain guard, never hit by the strictly-positive OHLCV fixtures).
    """

    spec = IndicatorSpec(
        name="ln",
        category="math_transform",
        aliases=("Natural Logarithm", "LN"),
        inputs=(CLOSE,),
        outputs=("ln",),
        talib_compatible=True,
        references=("TA-Lib LN",),
        doc="ref/ta_docs/math_transform/math_transforms.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return ln(df[CLOSE])
