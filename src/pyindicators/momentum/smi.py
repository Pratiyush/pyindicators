"""SMI Ergodic — William Blau's Stochastic Momentum Index (ergodic form).

The SMI Ergodic *is* the True Strength Index (double-smoothed momentum) on a unit scale, paired
with a signal EMA and their oscillator (SMI - signal). Composes ``momentum.tsi`` (our TSI is the
x100 form, so we rescale to the unit SMI convention). See ``ref/ta_docs/momentum/misc_momentum.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from .tsi import tsi


def smi(close: pd.Series, fast: int = 5, slow: int = 20, signal: int = 5) -> dict:
    """SMI Ergodic line, signal, and oscillator (TSI on a unit scale)."""
    # pandas-ta smi == tsi(fast, slow) with scalar=1; our tsi smooths slow-then-fast and x100.
    t = tsi(close, long=slow, short=fast, signal=signal)
    line = t["tsi"] / 100.0
    sig = t["tsi_signal"] / 100.0
    return {"smi": line, "smi_signal": sig, "smi_osc": line - sig}


@INDICATORS.register
class SMIErgodic(Indicator):
    """SMI Ergodic Indicator.

    What: double-smoothed momentum (TSI) on a unit scale with a signal line and oscillator.
    Best settings: fast 5, slow 20, signal 5 (Blau); zero-line and signal crosses flag momentum.
    Edge cases: flat window (zero |momentum|) -> guarded to NaN (inherited from TSI).
    Parity: pandas-ta ``smi`` (SMI/SMIs/SMIo).
    """

    spec = IndicatorSpec(
        name="smi",
        category="momentum",
        aliases=("SMI Ergodic", "Stochastic Momentum Index"),
        inputs=(CLOSE,),
        outputs=("smi", "smi_signal", "smi_osc"),
        bounds={"smi": (-1.0, 1.0), "smi_signal": (-1.0, 1.0)},
        references=("Blau", "pandas-ta smi"),
        doc="ref/ta_docs/momentum/misc_momentum.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        fast: int = Field(default=5, ge=1)
        slow: int = Field(default=20, ge=1)
        signal: int = Field(default=5, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return smi(df[CLOSE], p["fast"], p["slow"], p["signal"])
