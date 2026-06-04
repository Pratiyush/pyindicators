"""HT_TRENDMODE — Hilbert-Transform Trend vs Cycle Mode (Ehlers / TA-Lib)."""

from __future__ import annotations

import pandas as pd

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec

from ._hilbert import HT_START_63, LOOKBACK_63, hilbert_state, mask_lookback


def ht_trendmode(close: pd.Series) -> pd.Series:
    """Regime flag: 1 = trending market, 0 = cycling market (TA-Lib's 4-step test)."""
    state = hilbert_state(close, HT_START_63)
    return mask_lookback(state.trend_mode, LOOKBACK_63, close.index)


@INDICATORS.register
class HtTrendMode(Indicator):
    """Hilbert Transform — Trend vs Cycle Mode.

    What: a 0/1 regime classifier from Ehlers' Hilbert-Transform machinery. 1 means the
        market is trending (use trend-following tools), 0 means it is cycling (use
        oscillators). The flag flips to cycle on a sine/lead-sine crossover, when too few
        bars have passed since that crossover, or when the dominant-cycle phase advances at
        roughly the expected rate; it overrides to trend when price sits >=1.5% from the
        instantaneous trendline.
    Best settings: close only, no parameters; output is exactly 0 or 1.
    Edge cases: the first 63 bars are NaN (TA-Lib's lookback with the default unstable
        period of 0); the recurrence seeds at bar 37. TA-Lib returns an integer array whose
        warm-up region is filled with 0, so parity is checked only where our output is
        defined (index >= 63), where it matches bit-for-bit.
    Parity: TA-Lib ``HT_TRENDMODE``, exact 0/1 match on the defined region.
    """

    spec = IndicatorSpec(
        name="ht_trendmode",
        category="cycle",
        aliases=("Hilbert Transform Trend vs Cycle Mode", "HT_TRENDMODE"),
        inputs=(CLOSE,),
        outputs=("ht_trendmode",),
        bounds={"ht_trendmode": (0.0, 1.0)},
        talib_compatible=True,
        references=("TA-Lib HT_TRENDMODE", "Ehlers Rocket Science for Traders"),
        doc="ref/ta_docs/cycle/HilbertTransform.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return ht_trendmode(df[CLOSE])
