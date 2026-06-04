"""VWMACD — Volume-Weighted MACD (finta ``EV_MACD``, "Elastic Volume Weighted MACD").

What: MACD computed on two Elastic Volume-Weighted Moving Averages (EVWMA) instead of plain
price EMAs — the line is ``EVWMA(fast) - EVWMA(slow)`` and the signal is an EMA of that line.
The EVWMA approximates the average price paid per share over the last ``period`` bars via a
volume-driven recurrence ``e[i] = e[i-1]*(volsum-vol)/volsum + vol*close/volsum`` (Christian
Fries' eVWMA). Inputs ``close``/``volume``; outputs ``(vwmacd, vwmacd_signal)``.

Why a dedicated EVWMA helper (not ``base.ema``): finta's EV_MACD is *not* a volume-weighted
EMA — it is built from EVWMA (a stateful per-share-cost recurrence) and its signal uses
pandas ``ewm(adjust=True)`` (zero-warm-up, first-value seed), neither of which matches our
TA-Lib-seeded ``base.ema``. Replicating finta's exact math is the only way to get parity, so
we compose ``safe_divide`` for the guarded ratios and keep the recurrence local.

Edge cases: finta emits 0 (not NaN) during the rolling warm-up and *resets* the recurrence to
0 on any bar where ``(volsum-vol)/volsum == 0`` or ``vol*close/volsum == 0`` (e.g. a zero
volume window). We reproduce that exactly, so the warm-up region is 0-filled, not NaN-filled.

Defaults: fast 12, slow 26, signal 9 (classic MACD lengths; finta's own defaults are 20/40/9).
Causal: each bar depends only on rows ``<= i``. Stateful: the EVWMA recurrence is path-dependent.

Parity: finta ``TA.EV_MACD`` (bit-exact closed-form replication; verified rtol ~0 on both the
deterministic and real fixtures for 12/26/9 and 20/40/9).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, VOLUME, Indicator, IndicatorSpec, safe_divide


def evwma(close: pd.Series, volume: pd.Series, period: int) -> pd.Series:
    """Elastic Volume-Weighted Moving Average (finta ``EVWMA``).

    Approximates the average price paid per share over the last ``period`` bars via the
    recurrence ``e[i] = e[i-1]*x[i] + y[i]`` where ``x = (volsum - vol)/volsum`` and
    ``y = vol*close/volsum`` over a rolling ``period``-bar volume sum. Matching finta, the
    recurrence seeds at 0 and resets to 0 on any bar where ``x == 0`` or ``y == 0`` (which
    covers the rolling warm-up, where ``x`` is 0-filled, and any zero-volume window).
    """
    vol_sum = volume.rolling(window=period, min_periods=period).sum()
    # x is 0-filled (finta does x.fillna(0)); y keeps its warm-up NaN (finta leaves it).
    x = safe_divide(vol_sum - volume, vol_sum).fillna(0.0)
    y = safe_divide(volume * close, vol_sum)
    xv = x.to_numpy(dtype="float64")
    yv = y.to_numpy(dtype="float64")
    out = np.empty(xv.size, dtype="float64")
    prev = 0.0
    for i in range(xv.size):
        # NaN compares False, so a warm-up NaN ``y`` never triggers the reset on its own;
        # ``x == 0`` (0-filled warm-up) is what zeroes those bars, exactly as finta does.
        if xv[i] == 0.0 or yv[i] == 0.0:
            prev = 0.0
        else:
            prev = prev * xv[i] + yv[i]
        out[i] = prev
    return pd.Series(out, index=close.index)


def vwmacd(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> dict:
    """Volume-Weighted MACD line (EVWMA fast - slow) and its signal EMA."""
    macd = evwma(df[CLOSE], df[VOLUME], fast) - evwma(df[CLOSE], df[VOLUME], slow)
    # finta's signal: pandas ewm(span=signal, adjust=True) — first-value seed, no warm-up NaN.
    signal_line = macd.ewm(ignore_na=False, span=signal, adjust=True).mean()
    return {"vwmacd": macd, "vwmacd_signal": signal_line}


@INDICATORS.register
class VWMACD(Indicator):
    """Volume-Weighted MACD (Elastic Volume Weighted MACD).

    What: MACD of two EVWMAs — ``EVWMA(fast) - EVWMA(slow)`` with an EMA signal line.
    Best settings: 12/26/9 (classic MACD lengths); finta's own defaults are 20/40/9.
    Edge cases: 0 (not NaN) during warm-up; recurrence resets to 0 on zero-volume windows.
    Parity: finta ``TA.EV_MACD`` (bit-exact replication of EVWMA + adjust=True ewm signal).
    """

    spec = IndicatorSpec(
        name="vwmacd",
        category="volume",
        aliases=("Volume Weighted MACD", "Elastic Volume Weighted MACD", "EV_MACD"),
        inputs=(CLOSE, VOLUME),
        outputs=("vwmacd", "vwmacd_signal"),
        stateful=True,  # EVWMA is a path-dependent recurrence
        references=("finta EV_MACD", "finta EVWMA"),
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        fast: int = Field(default=12, ge=1)
        slow: int = Field(default=26, ge=1)
        signal: int = Field(default=9, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return vwmacd(df, p["fast"], p["slow"], p["signal"])
