"""FVE — Finite Volume Element (Markos Katsanos).

A money-flow indicator with two innovations over OBV-style accumulation: it blends
*intraday* placement (``close - hl2``) with *interday* drift (``diff`` of typical price),
and it ignores noise via a price threshold (``factor`` percent of close) before signing
volume +/-/0. The signed volume is summed over ``length`` bars and normalised by average
volume, giving a percentage-of-volume oscillator centred on zero.

Composes ``base.sma`` (the average-volume normaliser) and ``price_transform`` typical price.
Parity vs finta ``TA.FVE``. See ``ref/ta_docs/volume/FVE.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import (
    CLOSE,
    HIGH,
    INDICATORS,
    LOW,
    VOLUME,
    Indicator,
    IndicatorSpec,
    safe_divide,
)


def fve(df: pd.DataFrame, length: int = 22, factor: float = 0.3) -> pd.Series:
    """Finite Volume Element over ``length`` bars (percent-of-volume oscillator).

    Money flow ``mf = close - hl2 + diff(typical price)`` combines intraday position with
    inter-day drift. Volume is signed +1/-1/0 by a +/- ``factor*close/100`` deadband: a bar
    whose ``mf`` sits inside the band (or whose ``mf`` is NaN at warm-up) contributes 0.
    ``FVE = sum(signed volume, length) / (avg volume * length) * 100``.
    """
    high, low, close, volume = df[HIGH], df[LOW], df[CLOSE], df[VOLUME]
    hl2 = (high + low) / 2.0
    typical = (high + low + close) / 3.0
    money_flow = close - hl2 + typical.diff()  # intraday placement + inter-day drift

    # Deadband threshold; NaN warm-up bars fail both comparisons -> default 0 (matches finta).
    cutoff = factor * close / 100.0
    signed = np.select(
        [money_flow > cutoff, money_flow < -cutoff],
        [volume, -volume],
        default=0.0,
    )
    signed_volume = pd.Series(signed, index=df.index, dtype="float64")

    flow_sum = signed_volume.rolling(length, min_periods=length).sum()
    avg_volume = sma(volume, length)  # rolling mean over the same window
    return safe_divide(flow_sum, avg_volume * length) * 100.0


@INDICATORS.register
class FVE(Indicator):
    """Finite Volume Element.

    What: signed-volume money flow (intraday + inter-day, with a noise deadband) summed over
    N bars and scaled by average volume into a percentage oscillator around zero.
    Best settings: ``length`` 22, ``factor`` 0.3 (Katsanos); > 0 accumulation, < 0 distribution.
    Edge cases: ``mf`` inside +/-``factor*close/100`` (and the warm-up NaN bar) sign to 0;
    average volume 0 -> guarded to NaN.
    Parity: finta ``FVE`` (not in core TA-Lib / pandas-ta).
    """

    spec = IndicatorSpec(
        name="fve",
        category="volume",
        aliases=("Finite Volume Element",),
        inputs=(HIGH, LOW, CLOSE, VOLUME),
        outputs=("fve",),
        references=("Katsanos", "finta FVE"),
        doc="ref/ta_docs/volume/FVE.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=22, ge=1)
        factor: float = Field(default=0.3, ge=0.0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return fve(df, self.params["length"], self.params["factor"])
