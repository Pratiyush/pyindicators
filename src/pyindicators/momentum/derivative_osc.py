"""Derivative Oscillator — double-EMA-smoothed RSI vs its SMA signal (Constance Brown).

Constance Brown's refinement of the RSI: take RSI, smooth it with an EMA-of-EMA cascade,
then subtract a simple-moving-average signal line of that smoothed series. The result
oscillates around zero and combines RSI's momentum read with MACD-style histogram timing
(``dosc = s - signal``), turning earlier and cleaner than raw RSI.

Composes ``momentum.rsi`` + ``base.ema`` (the EMA-of-EMA smoother) + ``base.sma`` (the
signal). Never re-inlines that math. See ``ref/ta_docs/momentum/misc_momentum.md``.

Calculation (Brown's standard 14/5/3/9):
    r      = RSI(close, rsi_length)
    s      = EMA(EMA(r, ema1), ema2)
    signal = SMA(s, signal_length)
    dosc   = s - signal
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import ema, sma
from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec
from pyindicators.momentum.rsi import rsi


def derivative_osc(
    close: pd.Series,
    rsi_length: int = 14,
    ema1: int = 5,
    ema2: int = 3,
    signal_length: int = 9,
) -> dict:
    """Derivative Oscillator and its smoothed-RSI line + SMA signal.

    ``s`` is the double-EMA-smoothed RSI, ``signal`` its SMA, and ``dosc = s - signal``
    is the published oscillator. The EMA cascade seeds TA-Lib-style (SMA seed, inner
    warm-up NaNs skipped), so the warm-up converges exponentially.
    """
    smoothed = ema(ema(rsi(close, rsi_length), ema1), ema2)
    signal = sma(smoothed, signal_length)
    return {
        "derivative_osc": smoothed - signal,
        "do_smoothed": smoothed,
        "do_signal": signal,
    }


@INDICATORS.register
class DerivativeOscillator(Indicator):
    """Derivative Oscillator.

    What: Constance Brown's double-EMA-smoothed RSI minus its SMA signal — an RSI-based
        oscillator with MACD-histogram-style timing around a zero line.
    Best settings: RSI 14, EMA 5 then 3, signal SMA 9 (Brown); zero-line crosses and
        signal crosses are the triggers; divergence with price flags reversals.
    Edge cases: long warm-up (RSI + EMA cascade + SMA); a fully flat series -> RSI NaN ->
        all outputs NaN (undefined, not fabricated). Smoother than RSI but not bounded.
    Parity: closed-form vs an independent pandas-ta ``rsi``+``ema``+``sma`` cascade (no
        reference lib ships this indicator); tail+rtol absorbs the EMA-seed warm-up, which
        converges to machine precision.
    """

    spec = IndicatorSpec(
        name="derivative_osc",
        category="momentum",
        aliases=("Derivative Oscillator", "DOSC"),
        inputs=(CLOSE,),
        outputs=("derivative_osc", "do_smoothed", "do_signal"),
        talib_compatible=True,
        references=("Constance Brown", "pandas-ta rsi/ema/sma cascade"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        rsi_length: int = Field(default=14, ge=1)
        ema1: int = Field(default=5, ge=1)
        ema2: int = Field(default=3, ge=1)
        signal_length: int = Field(default=9, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return derivative_osc(df[CLOSE], p["rsi_length"], p["ema1"], p["ema2"], p["signal_length"])
