"""HT_PHASOR — Hilbert-Transform Phasor Components (Ehlers / TA-Lib)."""

from __future__ import annotations

import pandas as pd

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from ._hilbert import HT_START_32, LOOKBACK_32, hilbert_state, mask_lookback


def ht_phasor(close: pd.Series) -> dict[str, pd.Series]:
    """In-phase (I1) and quadrature (Q1) components of the Hilbert phasor."""
    state = hilbert_state(close, HT_START_32)
    return {
        "in_phase": mask_lookback(state.in_phase, LOOKBACK_32, close.index),
        "quadrature": mask_lookback(state.quadrature, LOOKBACK_32, close.index),
    }


@INDICATORS.register
class HtPhasor(Indicator):
    """Hilbert Transform — Phasor Components.

    What: the in-phase (I1) and quadrature (Q1) components of the analytic signal from
        Ehlers' Hilbert-Transform pipeline — the raw real/imaginary phasor whose angle the
        DCPERIOD/DCPHASE functions turn into a cycle period and phase.
    Best settings: close only, no parameters.
    Edge cases: long fixed warm-up — the first 32 bars are NaN (TA-Lib's lookback with the
        default unstable period of 0); the recurrence seeds at bar 12. The two components
        share that warm-up.
    Parity: TA-Lib ``HT_PHASOR`` (returns inphase, quadrature), bit-exact (max |Δ| ~2e-12).
    """

    spec = IndicatorSpec(
        name="ht_phasor",
        category="cycle",
        aliases=("Hilbert Transform Phasor Components", "HT_PHASOR"),
        inputs=(CLOSE,),
        outputs=("in_phase", "quadrature"),
        talib_compatible=True,
        references=("TA-Lib HT_PHASOR", "Ehlers Rocket Science for Traders"),
        doc="ref/ta_docs/cycle/HilbertTransform.md",
    )

    def _compute(self, df: pd.DataFrame) -> dict[str, pd.Series]:
        return ht_phasor(df[CLOSE])
