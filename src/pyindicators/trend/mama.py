"""MAMA — MESA Adaptive Moving Average (John Ehlers / TA-Lib ``MAMA``).

``MAMA`` and its slower companion ``FAMA`` (Following Adaptive MA) share the *first six
stages* of the Ehlers Hilbert-Transform pipeline documented in
:mod:`pyindicators.cycle._hilbert` (WMA(4) smooth -> period-adaptive detrender -> in-phase /
quadrature -> phasor + 0.2/0.8 EMA -> homodyne discriminator -> clamped+smoothed period).
Where ``HT_DCPERIOD`` then *double-smooths* the period, MAMA instead diverges: it derives the
instantaneous **phase** from the raw in-phase/quadrature pair, turns the bar-to-bar phase
change into an adaptive EMA gain ``alpha = fastlimit / max(deltaPhase, 1)`` (clamped down to
``slowlimit``), and runs two coupled EMAs:

    ``mama = alpha*price + (1-alpha)*mama_prev``
    ``fama = 0.5*alpha*mama + (1 - 0.5*alpha)*fama_prev``

So MAMA speeds up when the cycle phase is turning quickly and crawls (gain ``slowlimit``) in
quiet stretches. The recurrence seeds at bar 6 (``_HT_START``) and TA-Lib emits from bar 32
(``_LOOKBACK``); the warm-up between the two is a transient that converges to TA-Lib on the
tail (the seeded EMAs lose memory of the ``prev = 0`` start). See ``ref/ta_docs/trend/MAMA.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

# Ehlers 4-tap Hilbert FIR coefficients (shared with _hilbert.py) and the rad->deg factor.
_A = 0.0962
_B = 0.5769
_RAD = 180.0 / np.pi

#: Seed index for the MAMA recurrence (WMA(4) needs 3 look-backs, the FIR needs 6).
_HT_START = 6
#: TA-Lib emit lookback for MAMA/FAMA (default unstable period 0); earlier bars are NaN.
_LOOKBACK = 32


def _fir(buf: np.ndarray, i: int) -> float:
    """The shared Ehlers 4-tap Hilbert FIR ``a*x[i] + b*x[i-2] - b*x[i-4] - a*x[i-6]``.

    Caller multiplies the result by the period-adaptive gain. ``i >= 6`` is guaranteed by the
    seed index, so the look-backs never go negative.
    """
    return _A * buf[i] + _B * buf[i - 2] - _B * buf[i - 4] - _A * buf[i - 6]


def _mama_fama(
    close: pd.Series, fastlimit: float = 0.5, slowlimit: float = 0.05
) -> tuple[pd.Series, pd.Series]:
    """Compute the MAMA and FAMA lines (the shared recurrence used by both indicators).

    A faithful transcription of TA-Lib ``TA_MAMA``: the first six Hilbert stages are identical
    to :mod:`pyindicators.cycle._hilbert`, then the phase-rate adaptive EMA replaces the
    period double-smooth. Returns two float64 ``Series`` (``mama``, ``fama``) with the first
    :data:`_LOOKBACK` bars set to NaN (TA-Lib's emit convention); they converge to TA-Lib
    bit-exactly on the tail.
    """
    x = close.to_numpy(dtype="float64")
    n = x.size
    mama = np.full(n, np.nan)
    fama = np.full(n, np.nan)
    if n == 0:
        return pd.Series(mama, index=close.index), pd.Series(fama, index=close.index)

    smooth = np.zeros(n)
    detrend = np.zeros(n)
    i1 = np.zeros(n)  # InPhase
    q1 = np.zeros(n)  # Quadrature
    i2 = np.zeros(n)
    q2 = np.zeros(n)
    re = np.zeros(n)
    im = np.zeros(n)
    period = np.zeros(n)

    prev_phase = 0.0
    prev_mama = 0.0
    prev_fama = 0.0

    for i in range(n):
        if i >= 3:
            smooth[i] = (4.0 * x[i] + 3.0 * x[i - 1] + 2.0 * x[i - 2] + x[i - 3]) / 10.0

        if i < _HT_START:
            continue  # still seeding the WMA / FIR look-backs

        adj = 0.075 * period[i - 1] + 0.54

        detrend[i] = _fir(smooth, i) * adj
        q1[i] = _fir(detrend, i) * adj
        i1[i] = detrend[i - 3]
        j_i = _fir(i1, i) * adj
        j_q = _fir(q1, i) * adj

        # Phasor addition for 3-bar averaging, then 0.2/0.8 EMA on each component.
        i2[i] = 0.2 * (i1[i] - j_q) + 0.8 * i2[i - 1]
        q2[i] = 0.2 * (q1[i] + j_i) + 0.8 * q2[i - 1]

        # Homodyne discriminator (0.2/0.8-smoothed real/imag), then period via arctan.
        re[i] = 0.2 * (i2[i] * i2[i - 1] + q2[i] * q2[i - 1]) + 0.8 * re[i - 1]
        im[i] = 0.2 * (i2[i] * q2[i - 1] - q2[i] * i2[i - 1]) + 0.8 * im[i - 1]
        if im[i] != 0.0 and re[i] != 0.0:
            period[i] = 360.0 / (np.arctan(im[i] / re[i]) * _RAD)
        else:
            period[i] = period[i - 1]

        period[i] = min(period[i], 1.5 * period[i - 1])
        period[i] = max(period[i], 0.67 * period[i - 1])
        period[i] = min(max(period[i], 6.0), 50.0)
        period[i] = 0.2 * period[i] + 0.8 * period[i - 1]

        if not np.isfinite(period[i]):  # a NaN tick has propagated -> emit NaN, never adapt off it
            mama[i] = fama[i] = np.nan
            prev_mama = prev_fama = np.nan
            prev_phase = np.nan
            continue

        # Instantaneous phase from the raw in-phase/quadrature pair (NOT the smoothed i2/q2).
        if i1[i] != 0.0:
            phase = np.arctan(q1[i] / i1[i]) * _RAD
        else:
            phase = prev_phase

        delta_phase = prev_phase - phase
        prev_phase = phase
        if delta_phase < 1.0:
            delta_phase = 1.0

        alpha = fastlimit / delta_phase
        if alpha < slowlimit:
            alpha = slowlimit

        prev_mama = mama[i] = alpha * x[i] + (1.0 - alpha) * prev_mama
        prev_fama = fama[i] = 0.5 * alpha * mama[i] + (1.0 - 0.5 * alpha) * prev_fama

    mama[: min(_LOOKBACK, n)] = np.nan  # TA-Lib emit convention: NaN before the 32-bar lookback
    fama[: min(_LOOKBACK, n)] = np.nan
    return pd.Series(mama, index=close.index), pd.Series(fama, index=close.index)


def mama(close: pd.Series, fastlimit: float = 0.5, slowlimit: float = 0.05) -> dict:
    """Return the MAMA and FAMA lines as a ``{"mama": ..., "fama": ...}`` dict."""
    m, f = _mama_fama(close, fastlimit, slowlimit)
    return {"mama": m, "fama": f}


@INDICATORS.register
class MAMA(Indicator):
    """MESA Adaptive Moving Average (with its FAMA companion line).

    What: an adaptive EMA whose gain follows the dominant-cycle phase rate — fast (up to
        ``fastlimit``) when the phase turns quickly, slow (down to ``slowlimit``) in quiet
        markets; FAMA is a half-gain follower used for crossover signals.
    Best settings: fastlimit=0.5, slowlimit=0.05 (Ehlers/TA-Lib). MAMA crossing FAMA = signal.
    Edge cases: long fixed warm-up — the first 32 bars are NaN (TA-Lib's lookback with the
        default unstable period of 0); the recurrence seeds at bar 6 and converges on the tail.
    Parity: TA-Lib ``MAMA`` — bit-exact on the tail once the seeded EMAs settle.
    """

    spec = IndicatorSpec(
        name="mama",
        category="trend",
        aliases=("MESA Adaptive Moving Average", "MAMA"),
        inputs=(CLOSE,),
        outputs=("mama", "fama"),
        stateful=True,
        talib_compatible=True,
        references=("Ehlers MESA", "TA-Lib MAMA"),
        doc="ref/ta_docs/trend/MAMA.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        fastlimit: float = Field(default=0.5, gt=0.0, le=1.0)
        slowlimit: float = Field(default=0.05, gt=0.0, le=1.0)

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return mama(df[CLOSE], p["fastlimit"], p["slowlimit"])
