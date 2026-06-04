"""MACDEXT — MACD with configurable MA types (TA-Lib ``MACDEXT``, SMA-mode default).

Generalises MACD by letting the fast/slow/signal averages be any MA type. TA-Lib's
``MACDEXT`` defaults *all three* matypes to ``0`` (SMA) — NOT the EMA of the classic
``MACD`` — so the default math is::

    line   = SMA(close, fast) - SMA(close, slow)
    signal = SMA(line, signal)
    hist   = line - signal

Composes ``base.sma`` so the SMA warm-up convention flows through all three outputs. We keep
SMA as the default to match ``talib.MACDEXT`` exactly. See ``ref/ta_docs/trend/MACD.md``.

Parity: ``talib.MACDEXT`` (all matypes 0) is the oracle. Because every leg is a plain rolling
mean (non-recursive), agreement is exact up to float64 rounding on the finite overlap. Note
TA-Lib aligns the MACD line to the *combined* lookback (it withholds the line until the signal
also seeds), whereas our composition emits the line one signal-window earlier; masking to the
mutual finite overlap reconciles that purely-cosmetic warm-up difference.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec


def macdext(
    close: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> dict:
    """Return the SMA-mode MACDEXT line, signal line, and histogram.

    Mirrors ``talib.MACDEXT`` with all matypes left at their default ``0`` (SMA): the line is
    ``SMA(close, fast) - SMA(close, slow)``, the signal its ``signal``-period SMA, and the
    histogram their difference. All three share the SMA warm-up convention.
    """
    line = sma(close, fast) - sma(close, slow)
    signal_line = sma(line, signal)
    return {
        "macdext": line,
        "macdext_signal": signal_line,
        "macdext_hist": line - signal_line,
    }


@INDICATORS.register
class MACDEXT(Indicator):
    """MACD with configurable MA types (SMA-mode default).

    What: the MACD construction (fast-minus-slow average, its smoothing, their difference) but
        defaulting every leg to an SMA — exactly TA-Lib's ``MACDEXT`` with matypes ``0``.
    Best settings: 12/26/9 (classic). This is the SMA variant; use plain ``macd`` for the EMA
        construction or ``macdfix`` to pin 12/26.
    Edge cases: meaningful only after ~slow+signal bars; a constant series -> all zeros; the
        SMA warm-up flows identically to all three outputs; the line emits ``slow-1`` bars in
        but the signal not until ``slow+signal-2``.
    Parity: ``talib.MACDEXT`` (all matypes 0) — exact up to float64 rounding on the finite
        overlap (every leg is a plain rolling mean, so there is no recursive seeding drift).
    """

    spec = IndicatorSpec(
        name="macdext",
        category="trend",
        aliases=("MACD Extended", "MACDEXT"),
        inputs=(CLOSE,),
        outputs=("macdext", "macdext_signal", "macdext_hist"),
        talib_compatible=True,
        references=("Appel", "TA-Lib MACDEXT"),
        doc="ref/ta_docs/trend/MACD.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        fast: int = Field(default=12, ge=1)
        slow: int = Field(default=26, ge=1)
        signal: int = Field(default=9, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return macdext(df[CLOSE], p["fast"], p["slow"], p["signal"])
