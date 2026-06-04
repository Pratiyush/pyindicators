"""Shared Hilbert-Transform machinery — the exact TA-Lib HT_* / MAMA pipeline.

Every TA-Lib Hilbert-Transform function (``HT_DCPERIOD``, ``HT_DCPHASE``, ``HT_PHASOR``,
``HT_SINE``, ``HT_TRENDMODE``, ``HT_TRENDLINE``) and the MAMA/FAMA adaptive average share
one digital-signal-processing recurrence taken from John Ehlers' *Rocket Science for
Traders* (the "MESA" / homodyne-discriminator method). This module reproduces that
recurrence **bit-exactly** against TA-Lib (verified ``max |Δ|`` on the order of 1e-12..1e-10
on both the deterministic random walk and real AAPL daily closes) and exposes the per-bar
intermediates so each pattern file just selects the array it needs.

No ``@register`` here — this is a pure pandas/numpy helper. The recurrence is genuinely
sequential (each bar feeds the next through several EMAs), so the core is a single Python
loop over a NumPy buffer.

THE VERIFIED PIPELINE (constants, windows, lookback)
----------------------------------------------------
All arithmetic is in float64. ``adj`` below is TA-Lib's ``adjustedPrevPeriod``.

1.  **WMA(4) smooth of price** — ``smoothPrice[i] = (4*c[i] + 3*c[i-1] + 2*c[i-2]
    + c[i-3]) / 10``. Stored only once ``i >= ht_start`` (and ``i >= 3``).

2.  **Period-adaptive gain** — ``adj = 0.075 * period[i-1] + 0.54``. This single scalar
    multiplies the detrender and *all four* Hilbert FIR filters on the bar (this is the
    crux of TA-Lib parity — the gain is applied to detrend, q1, jI and jQ alike).

3.  **Hilbert detrender (4-tap FIR, Ehlers coefficients a=0.0962, b=0.5769)** —
    ``detrend[i] = (a*smoothPrice[i] + b*smoothPrice[i-2] - b*smoothPrice[i-4]
    - a*smoothPrice[i-6]) * adj``.

4.  **In-phase / quadrature** — the same 4-tap FIR is the 90° phase shifter:
    ``q1[i] = (a*detrend[i] + b*detrend[i-2] - b*detrend[i-4] - a*detrend[i-6]) * adj`` and
    ``i1[i] = detrend[i-3]`` (a pure 3-bar delay). Advancing I1/Q1 by 90° gives
    ``jI`` and ``jQ`` (the FIR applied to ``i1`` resp. ``q1``, times ``adj``).

5.  **Phasor + 0.2/0.8 EMA** — ``i2 = i1 - jQ``, ``q2 = q1 + jI``, each then smoothed
    ``x2[i] = 0.2*x2[i] + 0.8*x2[i-1]``.

6.  **Homodyne discriminator** — ``re = i2*i2[-1] + q2*q2[-1]``,
    ``im = i2*q2[-1] - q2*i2[-1]``, each 0.2/0.8-smoothed, then
    ``period = 360 / (atan(im/re) * 180/π)`` (carry the previous period if ``re`` or ``im``
    is exactly 0). The raw period is clamped: at most ``1.5*prev``, at least ``0.67*prev``,
    then hard-clamped to ``[6, 50]``.

7.  **Period double-smooth** — ``period[i] = 0.2*period[i] + 0.8*period[i-1]`` then the
    reported ``smoothPeriod[i] = 0.33*period[i] + 0.67*smoothPeriod[i-1]``.

8.  **DC phase** — over the last ``DCPeriod = max(int(smoothPeriod+0.5), 1)`` smoothed-price
    samples, accumulate ``real = Σ sin(2πj/DCPeriod)*smoothPrice[i-j]`` and
    ``imag = Σ cos(2πj/DCPeriod)*smoothPrice[i-j]`` for ``j = 0..DCPeriod-1``; then
    ``dcPhase = atan(real/imag)*180/π`` (with TA-Lib's incremental fallback when
    ``|imag|==0``), ``+90``, ``+360/smoothPeriod`` if positive, ``+180`` if ``imag<0``,
    and finally ``-360`` if ``> 315``.

9.  **Sine / lead-sine** — ``sine = sin(dcPhase°)``, ``leadSine = sin((dcPhase+45)°)``.

10. **Instantaneous trendline** — ``itrend = SMA(close, DCPeriod)`` (a same-window simple
    average) then a WMA(4) of ``itrend``: ``trendline[i] = (4*itrend[i] + 3*itrend[i-1]
    + 2*itrend[i-2] + itrend[i-3]) / 10`` (clamping the look-backs to ``itrend[0]`` for the
    very first bars).

11. **Trend mode** — TA-Lib's 4-step regime test (sine/lead-sine crossover resets the
    counter to cycle mode; too-few bars since the crossover → cycle; an expected-range phase
    advance → cycle; price ≥1.5% from the trendline → trend override).

WARM-UP vs LOOKBACK
-------------------
``ht_start`` is where the recurrence *seeds* (TA-Lib does the smoothing/priming there):
**12** for the 32-lookback group (DCPERIOD, PHASOR) and **37** for the 63-lookback group
(DCPHASE, SINE, TRENDMODE, TRENDLINE). TA-Lib then only *emits* values once ``i >=
lookback`` (32 resp. 63 with the default unstable period of 0); everything before that is
NaN. So each pattern computes the full recurrence from ``ht_start`` and masks indices
``< lookback`` to NaN via :func:`mask_lookback`. The seeded warm-up between ``ht_start`` and
``lookback`` is intentionally discarded — only ``i >= lookback`` matches TA-Lib (and it
does, bit-for-bit).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

# --- pipeline constants (see module docstring) -----------------------------------------
_A = 0.0962  # Ehlers Hilbert FIR coefficient a
_B = 0.5769  # Ehlers Hilbert FIR coefficient b
_RAD = 180.0 / np.pi  # radians -> degrees

#: Seed index for the 32-bar-lookback group (HT_DCPERIOD, HT_PHASOR).
HT_START_32 = 12
#: Seed index for the 63-bar-lookback group (HT_DCPHASE, HT_SINE, HT_TRENDMODE, HT_TRENDLINE).
HT_START_63 = 37
#: TA-Lib emit lookback for the DCPERIOD/PHASOR group (default unstable period 0).
LOOKBACK_32 = 32
#: TA-Lib emit lookback for the DCPHASE/SINE/TRENDMODE/TRENDLINE group.
LOOKBACK_63 = 63


@dataclass(frozen=True)
class HilbertState:
    """Per-bar Hilbert-Transform intermediates, each a float64 ``ndarray`` of length ``n``.

    Indices ``< ht_start`` hold 0.0 (the seeding region). Use :func:`mask_lookback` to apply
    TA-Lib's NaN-before-lookback convention before returning a pattern's output.
    """

    smooth_price: np.ndarray  # WMA(4) of close
    in_phase: np.ndarray  # I1 (raw in-phase component)
    quadrature: np.ndarray  # Q1 (raw quadrature component)
    smooth_period: np.ndarray  # the doubly-smoothed dominant-cycle period (HT_DCPERIOD)
    dc_phase: np.ndarray  # dominant-cycle phase in degrees (HT_DCPHASE)
    sine: np.ndarray  # sin(dc_phase)         (HT_SINE line)
    lead_sine: np.ndarray  # sin(dc_phase+45)    (HT_SINE lead line)
    trend_mode: np.ndarray  # 0=cycle / 1=trend  (HT_TRENDMODE)
    trendline: np.ndarray  # instantaneous trendline (HT_TRENDLINE)


def _fir(buf: np.ndarray, i: int) -> float:
    """The shared Ehlers 4-tap Hilbert FIR ``a*x[i] + b*x[i-2] - b*x[i-4] - a*x[i-6]``.

    Caller multiplies the result by ``adj``. ``i >= 6`` is guaranteed by the seed index.
    """
    return _A * buf[i] + _B * buf[i - 2] - _B * buf[i - 4] - _A * buf[i - 6]


def _run(close: np.ndarray, ht_start: int) -> HilbertState:
    """Execute the full Hilbert recurrence over ``close`` seeding at ``ht_start``.

    A faithful transcription of the TA-Lib HT pipeline (see module docstring). Returns every
    intermediate so the thin pattern wrappers can pick what they need; unused arrays cost
    almost nothing relative to the per-bar trig.
    """
    n = close.size
    smooth_price = np.zeros(n)
    detrend = np.zeros(n)
    i1 = np.zeros(n)  # InPhase
    q1 = np.zeros(n)  # Quadrature
    i2 = np.zeros(n)
    q2 = np.zeros(n)
    re = np.zeros(n)
    im = np.zeros(n)
    period = np.zeros(n)
    itrend = np.zeros(n)

    smooth_period = np.zeros(n)
    dc_phase = np.zeros(n)
    sine = np.zeros(n)
    lead_sine = np.zeros(n)
    trend_mode = np.zeros(n)
    trendline = np.zeros(n)

    # Cumulative close sum for the O(1) SMA inside the trendline step.
    csum = np.concatenate(([0.0], np.cumsum(close)))

    # Trend-mode carry state (matches TA-Lib's prev-bar bookkeeping).
    days_in_trend = 0
    prev_sine = 0.0
    prev_lead_sine = 0.0
    prev_dc_phase = 0.0

    for i in range(n):
        if i >= ht_start and i >= 3:
            smooth_price[i] = (
                4.0 * close[i] + 3.0 * close[i - 1] + 2.0 * close[i - 2] + close[i - 3]
            ) / 10.0

        if i < ht_start:
            continue  # still seeding; period/smooth_period stay 0.0

        adj = 0.075 * period[i - 1] + 0.54

        detrend[i] = _fir(smooth_price, i) * adj
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
        smooth_period[i] = 0.33 * period[i] + 0.67 * smooth_period[i - 1]

        sp = smooth_period[i]
        if not np.isfinite(sp):  # a NaN tick has propagated into the period -> emit NaN, never int(NaN)
            dc_phase[i] = sine[i] = lead_sine[i] = itrend[i] = trendline[i] = np.nan
            trend_mode[i] = np.nan
            prev_sine = prev_lead_sine = prev_dc_phase = np.nan
            continue
        dc_period = max(int(sp + 0.5), 1)

        # DC phase: discrete sine/cosine transform of the last `dc_period` smoothed prices.
        # `dc_period <= 50 <= ht_start..i`, so `i - j` never goes negative here.
        real_part = 0.0
        imag_part = 0.0
        for j in range(dc_period):
            ang = 2.0 * np.pi * j / dc_period
            w = smooth_price[i - j]
            real_part += np.sin(ang) * w
            imag_part += np.cos(ang) * w

        if abs(imag_part) > 0.0:
            phase = np.arctan(real_part / imag_part) * _RAD
        else:  # pragma: no cover - TA-Lib's incremental fallback when the imag part collapses
            phase = prev_dc_phase
            if real_part < 0.0:
                phase -= 90.0
            elif real_part > 0.0:
                phase += 90.0
        phase += 90.0
        if sp > 0.0:  # pragma: no branch - sp >= ~2 once past seeding (period clamp >= 6)
            phase += 360.0 / sp
        if imag_part < 0.0:
            phase += 180.0
        if phase > 315.0:
            phase -= 360.0
        dc_phase[i] = phase

        sine[i] = np.sin(phase / _RAD)
        lead_sine[i] = np.sin((phase + 45.0) / _RAD)

        # Instantaneous trendline: SMA(close, dc_period) then WMA(4) of that SMA.
        start = max(i - dc_period + 1, 0)
        itrend[i] = (csum[i + 1] - csum[start]) / dc_period
        # i >= ht_start >= 12, so the i-1..i-3 look-backs are always in range.
        trendline[i] = (
            4.0 * itrend[i] + 3.0 * itrend[i - 1] + 2.0 * itrend[i - 2] + itrend[i - 3]
        ) / 10.0

        # Trend mode (TA-Lib's 4-step regime classifier).
        trend = 1
        if (sine[i] > lead_sine[i] and prev_sine <= prev_lead_sine) or (
            sine[i] < lead_sine[i] and prev_sine >= prev_lead_sine
        ):
            days_in_trend = 0
            trend = 0
        days_in_trend += 1
        if days_in_trend < 0.5 * sp:
            trend = 0
        phase_diff = phase - prev_dc_phase
        if sp != 0.0 and 0.67 * 360.0 / sp < phase_diff < 1.5 * 360.0 / sp:
            trend = 0
        if trendline[i] != 0.0 and abs((smooth_price[i] - trendline[i]) / trendline[i]) >= 0.015:
            trend = 1
        trend_mode[i] = float(trend)

        prev_sine = sine[i]
        prev_lead_sine = lead_sine[i]
        prev_dc_phase = phase

    return HilbertState(
        smooth_price=smooth_price,
        in_phase=i1,
        quadrature=q1,
        smooth_period=smooth_period,
        dc_phase=dc_phase,
        sine=sine,
        lead_sine=lead_sine,
        trend_mode=trend_mode,
        trendline=trendline,
    )


def hilbert_state(close: pd.Series, ht_start: int) -> HilbertState:
    """Run the Hilbert recurrence on a close ``Series`` and return all intermediates.

    ``ht_start`` selects the seed index: :data:`HT_START_32` (12) for the DCPERIOD/PHASOR
    group, :data:`HT_START_63` (37) for the DCPHASE/SINE/TRENDMODE/TRENDLINE group. Apply
    :func:`mask_lookback` to a chosen array to get TA-Lib's NaN-before-lookback output.
    """
    return _run(close.to_numpy(dtype="float64"), ht_start)


def mask_lookback(values: np.ndarray, lookback: int, index: pd.Index) -> pd.Series:
    """Return ``values`` as a float64 ``Series`` with indices ``< lookback`` set to NaN.

    This is TA-Lib's emit convention: the recurrence seeds earlier (at ``ht_start``) but
    TA-Lib only reports values from ``lookback`` onwards. ``lookback`` is :data:`LOOKBACK_32`
    or :data:`LOOKBACK_63`.
    """
    out = np.asarray(values, dtype="float64").copy()
    out[: min(lookback, out.size)] = np.nan  # lookback is always 32 or 63 (> 0)
    return pd.Series(out, index=index)
