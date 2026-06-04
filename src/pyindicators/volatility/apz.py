"""Adaptive Price Zone (APZ) — volatility envelope (Lee Leibfarth, 2006).

A self-adjusting band built from *double-smoothed* EMAs at a short period derived from the
look-back: ``p = round(sqrt(length))``. The midline is ``EMA(EMA(close, p), p)`` and the
half-width is ``mult * EMA(EMA(high - low, p), p)`` — so the bands widen automatically as the
true range expands and tighten in quiet, choppy markets (its intended use, per Leibfarth's
"Trade With the Odds"). Composes ``base.ema``; the double-smoothing is just ``ema`` applied
twice, never re-inlined. See ``ref/ta_docs/volatility/APZ.md``.
"""

from __future__ import annotations

import math

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema
from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def apz(
    df: pd.DataFrame,
    length: int = 21,
    mult: float = 2.0,
    talib_compatible: bool = True,
) -> dict:
    """Adaptive Price Zone middle / upper / lower bands.

    The smoothing period is ``round(sqrt(length))`` (5 at the default ``length`` of 21); both
    the midline and the range are passed through that EMA twice (double-smoothing). The band
    half-width is ``mult`` times the double-smoothed high-low range, so it adapts to volatility.
    """
    period = max(1, round(math.sqrt(length)))  # Leibfarth's adaptive period; >=1 guard
    middle = ema(ema(df[CLOSE], period, talib_compatible), period, talib_compatible)
    rng = df[HIGH] - df[LOW]
    band = mult * ema(ema(rng, period, talib_compatible), period, talib_compatible)
    return {"apz_middle": middle, "apz_upper": middle + band, "apz_lower": middle - band}


@INDICATORS.register
class APZ(Indicator):
    """Adaptive Price Zone.

    What: a double-smoothed EMA midline with volatility-scaled bands whose width tracks the
        double-smoothed high-low range; tuned for non-trending, mean-reverting markets.
    Best settings: ``length`` 21 (-> EMA period 5), ``mult`` 2.0 (Leibfarth's defaults).
    Edge cases: a flat high==low series collapses the band to the midline (range 0); a frame
        shorter than the EMA double warm-up (``2*period - 1`` valid bars) is all NaN.
    Parity: no library oracle matches this exact form (finta's ``APZ`` uses a DEMA midline at
        the full ``length`` with ``adjust=True``); validated against the explicit double-EMA
        closed form in ``tests/parity/test_parity_apz.py``.
    """

    spec = IndicatorSpec(
        name="apz",
        category="volatility",
        aliases=("Adaptive Price Zone", "APZ"),
        inputs=(HIGH, LOW, CLOSE),
        outputs=("apz_middle", "apz_upper", "apz_lower"),
        talib_compatible=True,
        causal=True,
        references=("Leibfarth 2006", "finta APZ (variant)"),
        doc="ref/ta_docs/volatility/APZ.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=21, ge=1)
        mult: float = Field(default=2.0, gt=0)
        talib_compatible: bool = True

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return apz(df, p["length"], p["mult"], p["talib_compatible"])
