"""McGinley Dynamic — a self-adjusting smoother (John R. McGinley).

Hugs price far more tightly than an EMA by dividing the step by an adaptive denominator that
speeds the line up in downtrends and slows it in uptrends. No look-back window: it is a pure
recursion seeded with the first close. See ``ref/ta_docs/trend/misc_MA.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def mcgd(close: pd.Series, length: int = 10, c: float = 1.0) -> pd.Series:
    """McGinley Dynamic: md += (close - md) / (c * length * (close/md)^4)."""
    x = close.to_numpy(dtype="float64")
    n = x.size
    out = np.empty(n)
    if n == 0:
        return pd.Series(out, index=close.index)
    out[0] = x[0]
    # The recursion is an inherently unstable IIR: a near-zero divisor (floored to 1e-10) on a
    # huge gap can blow the line up to +/-inf. pandas-ta hits the same under numba; we silence
    # the resulting numpy warnings rather than spam them (values still match on real data).
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        for i in range(1, n):
            prev = out[i - 1]
            if prev != 0.0:
                denom = c * length * (x[i] / prev) ** 4
                if denom < 1e-10:  # guard the divisor (matches pandas-ta)
                    denom = 1e-10
                out[i] = prev + (x[i] - prev) / denom
            else:
                out[i] = x[i]
    return pd.Series(out, index=close.index)


@INDICATORS.register
class McGinleyDynamic(Indicator):
    """McGinley Dynamic.

    What: a moving average that minimizes price separation and whipsaws by adapting its step
        to the close/line ratio (faster in declines, slower in advances).
    Best settings: ``length`` 10, ``c`` 1 (sometimes 0.6 to track faster).
    Edge cases: starts at bar 0 (seeded with the first close, no warm-up NaN); denominator
        floored at 1e-10; a zero prior value resets the line to the close.
    Parity: pandas-ta ``mcgd``, exact.
    """

    spec = IndicatorSpec(
        name="mcgd",
        category="trend",
        aliases=("McGinley Dynamic",),
        inputs=(CLOSE,),
        outputs=("mcgd",),
        stateful=True,
        references=("McGinley", "pandas-ta mcgd"),
        doc="ref/ta_docs/trend/misc_MA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=10, ge=1)
        c: float = Field(default=1.0, gt=0.0, le=1.0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        p = self.params
        return mcgd(df[CLOSE], p["length"], p["c"])
