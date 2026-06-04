"""DeMarker (DeM) — momentum oscillator (Thomas DeMark).

Compares each bar's high/low extension against the prior bar to gauge buying vs selling
demand, then normalises to [0, 1]: ``DeMax = max(H - prevH, 0)``, ``DeMin = max(prevL - L, 0)``,
``DeM = SMA(DeMax, N) / (SMA(DeMax, N) + SMA(DeMin, N))``. Composes ``base.sma`` and
``core.safe_divide``. Values near 0.7 flag overbought, near 0.3 oversold.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec, safe_divide


def demarker(high: pd.Series, low: pd.Series, length: int = 14) -> pd.Series:
    """DeMarker over ``length`` bars, bounded [0, 1].

    Edge handling falls out of the arithmetic: a window with no higher highs and no lower
    lows (e.g. a flat series) gives ``SMA(DeMax) == SMA(DeMin) == 0`` -> 0/0, which
    ``safe_divide`` maps to NaN (undefined, not fabricated). The leading ``diff`` NaN
    propagates through ``clip``, so the first ``length`` bars are NaN (warm-up).
    """
    de_max = (high - high.shift(1)).clip(lower=0.0)  # higher highs only (else 0)
    de_min = (low.shift(1) - low).clip(lower=0.0)  # lower lows only (else 0)
    sma_max = sma(de_max, length)
    sma_min = sma(de_min, length)
    return safe_divide(sma_max, sma_max + sma_min)  # NaN where both averages are 0


@INDICATORS.register
class DeMarker(Indicator):
    """DeMarker.

    What: DeMark's bounded (0-1) demand oscillator — averaged higher-high vs lower-low
    extension over ``length`` bars.
    Best settings: 14 (DeMark); bands 0.7 overbought, 0.3 oversold.
    Edge cases: a window with no higher highs and no lower lows (flat series) -> 0/0,
    guarded to NaN; a pure up-leg (no lower lows) -> 1; a pure down-leg -> 0.
    Parity: no reference-library implementation exists (TA-Lib/pandas-ta/finta/ta lack
    DeMarker); validated against the explicit closed-form definition above.
    """

    spec = IndicatorSpec(
        name="demarker",
        category="momentum",
        aliases=("DeMarker", "DeM", "DEM"),
        inputs=(HIGH, LOW),
        outputs=("demarker",),
        bounds={"demarker": (0.0, 1.0)},
        references=("DeMark 1994", "DeMarker oscillator"),
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=14, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return demarker(df[HIGH], df[LOW], self.params["length"])
