"""MSW — Mesa Sine Wave (John Ehlers, *Rocket Science For Traders*, 2001).

Not the homodyne Hilbert pipeline that drives the ``HT_*`` family: MSW is the simpler,
fixed-window Tulip-Indicators formulation. Over the trailing ``period`` bars it runs a single
DFT bin (the discrete sine/cosine transform at the period frequency) to estimate the dominant
phase, then emits two oscillators bounded to ``[-1, 1]``:

- ``msw_sine`` = ``sin(phase)``
- ``msw_lead`` = ``sin(phase + 45°)``

A sine/lead crossover marks a cycle turning point. The phase estimate uses ``j = 0`` for the
newest bar (the window is read newest-first), the same convention Tulip Indicators / pandas-ta
(`pandas_ta_classic.cycles.msw`) use, which this matches exactly. The first ``period`` bars are
NaN (the window is not yet full). See ``ref/ta_docs/cycle/HilbertTransform.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

_TPI = 2.0 * np.pi
_QUARTER = np.pi / 4.0  # the 45-degree lead offset, in radians


def msw(close: pd.Series, period: int = 5) -> dict[str, pd.Series]:
    """Mesa Sine Wave sine and lead lines over a trailing ``period``-bar window.

    For each bar ``i >= period`` the trailing window (newest-first, so ``j = 0`` is ``close[i]``)
    is correlated against ``cos`` and ``sin`` at the period frequency to get a real/imag pair;
    the phase is recovered with ``arctan`` (degenerate-quadrant handling for tiny real parts),
    shifted into ``[0, 2π)``, and turned into ``sin(phase)`` and ``sin(phase + 45°)``.
    """
    arr = close.to_numpy(dtype="float64")
    n = arr.size
    sine = np.full(n, np.nan)
    lead = np.full(n, np.nan)

    j_arr = np.arange(period, dtype="float64")
    cos_w = np.cos(_TPI * j_arr / period)
    sin_w = np.sin(_TPI * j_arr / period)

    for i in range(period, n):
        window = arr[i - period + 1 : i + 1][::-1]  # newest-first -> j=0 is the latest bar
        real_part = float(np.dot(window, cos_w))
        imag_part = float(np.dot(window, sin_w))

        if abs(real_part) > 0.001:
            phase = np.arctan(imag_part / real_part)
        else:  # real part collapses -> pin to the +/- vertical axis by the imag sign
            phase = (np.pi / 2.0) * (-1.0 if imag_part < 0.0 else 1.0)

        if real_part < 0.0:
            phase += np.pi
        phase += np.pi / 2.0
        # The reference also wraps phase into [0, 2pi) here, but after the arctan/degenerate
        # handling and these +pi/+pi/2 shifts the phase is provably already in (0, 2pi): the
        # arctan branch lands in (0, 2pi) and the degenerate axis-pin gives exactly 0 or pi.
        # sin() is 2pi-periodic anyway, so the (dead) wraps are omitted with no value change.

        sine[i] = np.sin(phase)
        lead[i] = np.sin(phase + _QUARTER)

    return {
        "msw_sine": pd.Series(sine, index=close.index),
        "msw_lead": pd.Series(lead, index=close.index),
    }


@INDICATORS.register
class MesaSineWave(Indicator):
    """Mesa Sine Wave (MSW).

    What: a two-line cycle oscillator (sine and a 45-degree lead) from Ehlers; a single-bin
        DFT over the trailing window estimates the dominant phase. Sine/lead crossovers flag
        cycle turning points; both lines stay in ``[-1, 1]``.
    Best settings: ``period`` 5 (Tulip/pandas-ta default); larger periods react more slowly.
    Edge cases: ``period`` floored to 5 when <= 1 (matches the reference); the first ``period``
        bars are NaN (window not yet full); a near-zero real part snaps the phase to the
        vertical axis by the imaginary sign.
    Parity: pandas-ta-classic ``msw`` (native, Tulip-Indicators formula), exact.
    """

    spec = IndicatorSpec(
        name="msw",
        category="cycle",
        aliases=("Mesa Sine Wave", "MSW"),
        inputs=(CLOSE,),
        outputs=("msw_sine", "msw_lead"),
        bounds={"msw_sine": (-1.0, 1.0), "msw_lead": (-1.0, 1.0)},
        references=("Ehlers Rocket Science for Traders", "Tulip Indicators msw", "pandas-ta msw"),
        doc="ref/ta_docs/cycle/HilbertTransform.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        period: int = Field(default=5, ge=2)

    def _compute(self, df: pd.DataFrame) -> dict[str, pd.Series]:
        return msw(df[CLOSE], self.params["period"])
