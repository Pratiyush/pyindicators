"""HT_DCPERIOD — Hilbert-Transform Dominant Cycle Period (Ehlers / TA-Lib)."""

from __future__ import annotations

import pandas as pd

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from ._hilbert import HT_START_32, LOOKBACK_32, hilbert_state, mask_lookback


def ht_dcperiod(close: pd.Series) -> pd.Series:
    """Dominant-cycle length in bars (the doubly-smoothed homodyne period)."""
    state = hilbert_state(close, HT_START_32)
    return mask_lookback(state.smooth_period, LOOKBACK_32, close.index)


@INDICATORS.register
class HtDcPeriod(Indicator):
    """Hilbert Transform — Dominant Cycle Period.

    What: the length (in bars) of the dominant market cycle, via Ehlers' Hilbert-Transform
        homodyne discriminator. Used to make other indicators adaptive.
    Best settings: close only, no parameters; clamped to 6..50 bars internally.
    Edge cases: long fixed warm-up — the first 32 bars are NaN (TA-Lib's lookback with the
        default unstable period of 0); the recurrence seeds at bar 12.
    Parity: TA-Lib ``HT_DCPERIOD``, bit-exact (max |Δ| ~3e-12).
    """

    spec = IndicatorSpec(
        name="ht_dcperiod",
        category="cycle",
        aliases=("Hilbert Transform Dominant Cycle Period", "HT_DCPERIOD"),
        inputs=(CLOSE,),
        outputs=("ht_dcperiod",),
        bounds={"ht_dcperiod": (6.0, 50.0)},
        talib_compatible=True,
        references=("TA-Lib HT_DCPERIOD", "Ehlers Rocket Science for Traders"),
        doc="ref/ta_docs/cycle/HilbertTransform.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return ht_dcperiod(df[CLOSE])
