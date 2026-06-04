"""Fisher Transform — sharpen turning points by Gaussianising price (John Ehlers).

Normalises HL2 to -0.5..0.5 over a window, smooths it, then applies the inverse-Fisher
``0.5*ln((1+x)/(1-x))`` (with a recursive carry) so extremes become sharp, near-symmetric
peaks. Stateful recursion; the signal line is the Fisher lagged by ``signal``. See
``ref/ta_docs/momentum/misc_momentum.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def fisher(df: pd.DataFrame, length: int = 9, signal: int = 1) -> dict:
    """Fisher Transform line and its signal (Fisher lagged by ``signal``)."""
    mid = (df[HIGH] + df[LOW]) / 2.0  # HL2
    hh = mid.rolling(length, min_periods=length).max()
    ll = mid.rolling(length, min_periods=length).min()
    hlr = (hh - ll).mask(lambda s: s < 0.001, 0.001)  # avoid divide-by-tiny-range
    pos = ((mid - ll) / hlr - 0.5).to_numpy()
    n = mid.size
    out = np.full(n, np.nan)
    if n >= length:
        out[length - 1] = 0.0
        v = 0.0
        for i in range(length, n):
            v = 0.66 * pos[i] + 0.67 * v
            if v < -0.99:  # snap to the edge once outside +/-0.99 (matches pandas-ta)
                v = -0.999
            elif v > 0.99:
                v = 0.999
            out[i] = 0.5 * (np.log((1.0 + v) / (1.0 - v)) + out[i - 1])
    line = pd.Series(out, index=df.index)
    return {"fisher": line, "fisher_signal": line.shift(signal)}


@INDICATORS.register
class FisherTransform(Indicator):
    """Fisher Transform.

    What: a leading oscillator that turns the price distribution Gaussian so tops/bottoms
        become sharp, easily-dated extremes.
    Best settings: ``length`` 9, ``signal`` 1; crossovers of Fisher and its signal flag turns.
    Edge cases: HL2 range floored at 0.001; the transform input is clamped to +/-0.999 before
        the log; first ``length`` bars NaN (seeded at 0 on the boundary).
    Parity: pandas-ta ``fisher``, exact.
    """

    spec = IndicatorSpec(
        name="fisher",
        category="momentum",
        aliases=("Fisher Transform", "FISHT"),
        inputs=(HIGH, LOW),
        outputs=("fisher", "fisher_signal"),
        stateful=True,
        references=("Ehlers", "pandas-ta fisher"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=9, ge=1)
        signal: int = Field(default=1, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        return fisher(df, self.params["length"], self.params["signal"])
