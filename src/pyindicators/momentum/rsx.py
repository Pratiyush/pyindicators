"""RSX — Relative Strength Xtra (Jurik-inspired smoother RSI).

A noise-reduced RSI: gains/losses are pushed through a six-deep cascade of paired,
zero-lag (``1.5*ema1 - 0.5*ema2``) smoothers driven by a single ``f18 = 3/(length+2)``
coefficient, then mapped to ``(v14/v20 + 1) * 50`` and clamped to [0, 100]. The recurrence
is path-dependent and seeded in-place (the ``length-1`` bar is 0.0; early bars read 50.0
until the warm-up counter clears), so this is a faithful state-machine port of pandas-ta's
``rsx``. See ``ref/ta_docs/momentum/misc_momentum.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

# Below this, the smoothed magnitude ``v20`` is treated as zero -> output pinned to 50
# (pandas-ta's literal guard against the 0/0 that a flat/quiet window would otherwise make).
_V20_EPS = 1e-10


def _rsx_loop(c_arr: np.ndarray, length: int, m: int) -> np.ndarray:
    """Port of pandas-ta ``_rsx_loop``: the stateful six-stage RSX cascade.

    Variable names mirror the published ProRealCode/Jurik implementation verbatim so the
    recursion can be checked line-for-line against the reference; do not rename them.
    """
    result = np.full(m, np.nan, dtype="float64")
    if m < length:  # too short to seed: the reference's verify_series bails -> all NaN
        return result
    result[length - 1] = 0.0
    vc = v1c = v4 = v8 = v10 = v14 = v18 = v20 = 0.0
    f0 = f8 = f10 = f18 = f20 = f28 = f30 = f38 = f40 = 0.0
    f48 = f50 = f58 = f60 = f68 = f70 = f78 = f80 = f88 = f90 = 0.0
    for i in range(length, m):
        if f90 == 0:
            f90 = 1.0
            f0 = 0.0
            f88 = length - 1.0 if length - 1.0 >= 5 else 5.0
            f8 = 100.0 * c_arr[i]
            f18 = 3.0 / (length + 2.0)
            f20 = 1.0 - f18
        else:
            f90 = f88 + 1 if f88 <= f90 else f90 + 1
            f10 = f8
            f8 = 100.0 * c_arr[i]
            v8 = f8 - f10
            f28 = f20 * f28 + f18 * v8
            f30 = f18 * f28 + f20 * f30
            vc = 1.5 * f28 - 0.5 * f30
            f38 = f20 * f38 + f18 * vc
            f40 = f18 * f38 + f20 * f40
            v10 = 1.5 * f38 - 0.5 * f40
            f48 = f20 * f48 + f18 * v10
            f50 = f18 * f48 + f20 * f50
            v14 = 1.5 * f48 - 0.5 * f50
            f58 = f20 * f58 + f18 * abs(v8)
            f60 = f18 * f58 + f20 * f60
            v18 = 1.5 * f58 - 0.5 * f60
            f68 = f20 * f68 + f18 * v18
            f70 = f18 * f68 + f20 * f70
            v1c = 1.5 * f68 - 0.5 * f70
            f78 = f20 * f78 + f18 * v1c
            f80 = f18 * f78 + f20 * f80
            v20 = 1.5 * f78 - 0.5 * f80
            if f88 >= f90 and f8 != f10:
                f0 = 1.0
            if f88 == f90 and f0 == 0.0:
                f90 = 0.0
        if f88 < f90 and v20 > _V20_EPS:
            v4 = (v14 / v20 + 1.0) * 50.0
            if v4 > 100.0:  # pragma: no cover - faithful-port defensive clamp; |v14|<=v20 caps v4 at 100
                v4 = 100.0
            if v4 < 0.0:
                v4 = 0.0
        else:
            v4 = 50.0
        result[i] = v4
    return result


def rsx(close: pd.Series, length: int = 14) -> pd.Series:
    """Relative Strength Xtra of ``close`` over ``length`` bars, bounded [0, 100].

    Path-dependent: the value at bar ``i`` is the state of the smoothing cascade after
    folding in every bar up to ``i``. Bars before ``length-1`` are NaN (warm-up), ``length-1``
    seeds to 0.0, and a flat/quiet stretch reads 50.0 (the neutral guard).
    """
    arr = close.to_numpy(dtype="float64")
    return pd.Series(_rsx_loop(arr, length, arr.size), index=close.index)


@INDICATORS.register
class RSX(Indicator):
    """Relative Strength Xtra (RSX).

    What: a Jurik-inspired, heavily smoothed RSI (0-100) that cuts noise with a six-deep
        cascade of zero-lag smoothers while adding only slight lag.
    Best settings: 14 (as RSI); shorter for a faster, noisier line. Bands 80/20.
    Edge cases: < ``length`` bars -> all NaN; the ``length-1`` bar seeds to 0.0; a flat or
        very quiet window reads the neutral 50.0.
    Parity: pandas-ta ``rsx`` exactly (faithful port of the stateful cascade).
    """

    spec = IndicatorSpec(
        name="rsx",
        category="momentum",
        aliases=("Relative Strength Xtra", "Jurik RSX"),
        inputs=(CLOSE,),
        outputs=("rsx",),
        bounds={"rsx": (0.0, 100.0)},
        stateful=True,
        references=("Jurik Research", "ProRealCode Jurik RSX", "pandas-ta rsx"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return rsx(df[CLOSE], self.params["length"])
