"""EBSW — Even Better Sinewave (John Ehlers, *Cycle Analytics for Traders* 2014).

A cycle oscillator (NOT part of the Hilbert-Transform HT_* machinery in ``_hilbert.py``).
The pipeline is a high-pass detrender followed by a SuperSmoother low-pass filter, then a
3-bar wave/power accumulation that normalises the smoothed wave by the RMS of its power:

1.  **High-pass filter** removes cyclic components longer than ``length`` bars::

        alpha1 = (1 - sin(360/length)) / cos(360/length)
        HP[i]  = 0.5*(1 + alpha1)*(close[i] - close[i-1]) + alpha1*HP[i-1]

2.  **SuperSmoother** (Ehlers eq. 3-3, a 2-pole low-pass) with the ``bars`` constant::

        a1 = exp(-sqrt(2)*pi/bars);  b1 = 2*a1*cos(sqrt(2)*180/bars)
        c2 = b1;  c3 = -a1*a1;  c1 = 1 - c2 - c3
        Filt[i] = c1*(HP[i] + HP[i-1])/2 + c2*Filt[i-1] + c3*Filt[i-2]

3.  **3-bar wave / power**, then normalise to the square root of the average power::

        Wave = (Filt[i] + Filt[i-1] + Filt[i-2]) / 3
        Pwr  = (Filt[i]^2 + Filt[i-1]^2 + Filt[i-2]^2) / 3
        ebsw = Wave / sqrt(Pwr)   (0 when Pwr <= 0)

The output is a bounded oscillator in roughly ``[-1, 1]``.

Fidelity note: the reference (``pandas_ta_classic.ebsw``) feeds *degrees* straight into
NumPy ``sin``/``cos`` (which expect radians) when forming ``alpha1`` and ``b1`` — i.e.
``sin(360/length)`` is ``sin(9.0 radians)`` for the default. That is a quirk of the published
implementation, but it is the definition we match bit-for-bit, so it is reproduced verbatim.

Warm-up: the reference emits NaN for the first ``length - 1`` bars and a seed ``0.0`` at index
``length - 1`` (the recurrence proper starts at bar ``length``); both are reproduced exactly.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

_RT2 = np.sqrt(2.0)


def ebsw(close: pd.Series, length: int = 40, bars: int = 10) -> pd.Series:
    """Even Better Sinewave of ``close``.

    ``length`` is the maximum detectable cycle/trend period (high-pass cutoff); the reference
    requires ``> 38`` and falls back to ``40`` otherwise. ``bars`` is the SuperSmoother
    low-pass period (``> 0``, else ``10``). The first ``length - 1`` bars are NaN with a
    ``0.0`` seed at index ``length - 1``, matching ``pandas_ta_classic.ebsw``.
    """
    length = int(length) if length and length > 38 else 40
    bars = int(bars) if bars and bars > 0 else 10

    values = close.to_numpy(dtype="float64")
    n = values.size
    out = np.full(n, np.nan)
    if n > length - 1:
        out[length - 1] = 0.0

    # All filter constants are period-only (no per-bar adaptation), so hoist them out.
    alpha1 = (1.0 - np.sin(360.0 / length)) / np.cos(360.0 / length)
    a1 = np.exp(-_RT2 * np.pi / bars)
    b1 = 2.0 * a1 * np.cos(_RT2 * 180.0 / bars)
    c2 = b1
    c3 = -a1 * a1
    c1 = 1.0 - c2 - c3

    last_close = 0.0
    last_hp = 0.0
    filt_2 = 0.0  # Filt[i-2]
    filt_1 = 0.0  # Filt[i-1]

    for i in range(length, n):
        hp = 0.5 * (1.0 + alpha1) * (values[i] - last_close) + alpha1 * last_hp
        filt = c1 * (hp + last_hp) / 2.0 + c2 * filt_1 + c3 * filt_2

        wave = (filt + filt_1 + filt_2) / 3.0
        pwr = (filt * filt + filt_1 * filt_1 + filt_2 * filt_2) / 3.0
        # Guard the normalisation: a flat warm-up leaves Pwr == 0 (the reference's policy).
        out[i] = wave / np.sqrt(pwr) if pwr > 0.0 else 0.0

        filt_2 = filt_1
        filt_1 = filt
        last_hp = hp
        last_close = values[i]

    return pd.Series(out, index=close.index)


@INDICATORS.register
class Ebsw(Indicator):
    """Even Better Sinewave (EBSW).

    What: an Ehlers cycle oscillator — a high-pass detrender feeding a SuperSmoother, then a
        3-bar wave normalised by the RMS of its power. Bounded in roughly [-1, 1]; the longest
        detectable trend is capped by ``length``.
    Best settings: ``length`` 40 (40-48 behave as designed; minimum 39), ``bars`` 10.
    Edge cases: first ``length-1`` bars NaN with a 0.0 seed at index ``length-1``; the
        high-pass/SuperSmoother constants feed degrees into sin/cos verbatim (see module
        docstring) to stay bit-exact with the reference.
    Parity: pandas-ta(-classic) ``ebsw`` (max |Δ| 0 on synthetic and real frames).
    """

    spec = IndicatorSpec(
        name="ebsw",
        category="cycle",
        aliases=("Even Better Sinewave", "EBSW"),
        inputs=(CLOSE,),
        outputs=("ebsw",),
        bounds={"ebsw": (-1.0, 1.0)},
        references=("pandas-ta ebsw", "Ehlers Cycle Analytics for Traders"),
        doc="ref/ta_docs/cycle/ebsw.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=40, ge=39)
        bars: int = Field(default=10, ge=1)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return ebsw(df[CLOSE], self.params["length"], self.params["bars"])
