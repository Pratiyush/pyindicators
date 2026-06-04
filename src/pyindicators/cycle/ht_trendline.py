"""HT_TRENDLINE — Hilbert-Transform Instantaneous Trendline (Ehlers / TA-Lib).

An Overlap Study (a smoothed price overlay), not a cycle oscillator: a WMA(4) of the
adaptive SMA(close, DCPeriod). Listed under Overlap Studies in TA-Lib.
"""

from __future__ import annotations

import pandas as pd

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from ._hilbert import HT_START_63, LOOKBACK_63, hilbert_state, mask_lookback


def ht_trendline(close: pd.Series) -> pd.Series:
    """Instantaneous trendline: WMA(4) of the dominant-cycle-length SMA of close."""
    state = hilbert_state(close, HT_START_63)
    return mask_lookback(state.trendline, LOOKBACK_63, close.index)


@INDICATORS.register
class HtTrendline(Indicator):
    """Hilbert Transform — Instantaneous Trendline.

    What: a price-overlay trendline — a 4-bar WMA of the simple average of close over the
        current dominant-cycle length — that hugs price with minimal lag in trends.
    Best settings: close only, no parameters; >=100 bars of warm-up recommended for stability.
    Edge cases: this is an overlay, NOT an oscillator. The first 63 bars are NaN (TA-Lib's
        lookback with the default unstable period of 0); the recurrence seeds at bar 37.
    Parity: TA-Lib ``HT_TRENDLINE``, bit-exact (max |Δ| ~1e-12).
    """

    spec = IndicatorSpec(
        name="ht_trendline",
        category="cycle",
        aliases=("Hilbert Transform Instantaneous Trendline", "HT_TRENDLINE"),
        inputs=(CLOSE,),
        outputs=("ht_trendline",),
        talib_compatible=True,
        references=("TA-Lib HT_TRENDLINE", "Ehlers Rocket Science for Traders"),
        doc="ref/ta_docs/cycle/HilbertTransform.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return ht_trendline(df[CLOSE])
