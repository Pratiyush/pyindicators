"""HT_DCPHASE — Hilbert-Transform Dominant Cycle Phase (Ehlers / TA-Lib)."""

from __future__ import annotations

import pandas as pd

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from ._hilbert import HT_START_63, LOOKBACK_63, hilbert_state, mask_lookback


def ht_dcphase(close: pd.Series) -> pd.Series:
    """Dominant-cycle phase in degrees (~0/360 = cycle low, ~180 = cycle high)."""
    state = hilbert_state(close, HT_START_63)
    return mask_lookback(state.dc_phase, LOOKBACK_63, close.index)


@INDICATORS.register
class HtDcPhase(Indicator):
    """Hilbert Transform — Dominant Cycle Phase.

    What: the phase (in degrees) of the dominant market cycle, from the discrete
        sine/cosine transform of the smoothed price over the current cycle length.
        ~0/360 marks a cycle low, ~180 a cycle high.
    Best settings: close only, no parameters.
    Edge cases: the phase is wrapped so values above 315 wrap down by 360 (so the output can
        be mildly negative). The first 63 bars are NaN (TA-Lib's lookback with the default
        unstable period of 0); the recurrence seeds at bar 37.
    Parity: TA-Lib ``HT_DCPHASE``, bit-exact (max |Δ| ~5e-11).
    """

    spec = IndicatorSpec(
        name="ht_dcphase",
        category="cycle",
        aliases=("Hilbert Transform Dominant Cycle Phase", "HT_DCPHASE"),
        inputs=(CLOSE,),
        outputs=("ht_dcphase",),
        talib_compatible=True,
        references=("TA-Lib HT_DCPHASE", "Ehlers Rocket Science for Traders"),
        doc="ref/ta_docs/cycle/HilbertTransform.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return ht_dcphase(df[CLOSE])
