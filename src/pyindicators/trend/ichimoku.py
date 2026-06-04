"""Ichimoku Kinko Hyo — the "one-glance equilibrium chart" (Goichi Hosoda, pre-WWII).

Four midprice lines built from rolling high/low extremes:

- ``tenkan`` (Tenkan-sen / Conversion Line)  = midprice over ``tenkan`` bars (default 9),
- ``kijun``  (Kijun-sen / Base Line)         = midprice over ``kijun`` bars (default 26),
- ``span_a`` (Senkou Span A / Leading Span A) = (tenkan + kijun) / 2,
- ``span_b`` (Senkou Span B / Leading Span B) = midprice over ``senkou`` bars (default 52),

where ``midprice(n) = (rollmax(high, n) + rollmin(low, n)) / 2``.

CAUSALITY (no look-ahead): the textbook chart plots Span A/B shifted ``kijun`` bars into the
FUTURE (the "cloud" / kumo leads price). That forward shift is pure look-ahead — at bar ``i``
the plotted cloud value was computed from data at bar ``i - kijun``, so reading it as a feature
at bar ``i`` would leak the future. We therefore emit the CURRENT-bar (UNSHIFTED) lines and set
``causal=True``: every value at bar ``i`` depends only on rows ``<= i``. A downstream backtester
that wants the visual cloud can shift these forward itself; the engine must stay causal.

Composes the same rolling-extrema midprice used by Donchian. See ``ref/ta_docs/trend/Ichimoku.md``.
"""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import HIGH, INDICATORS, LOW, Indicator, IndicatorSpec


def _midprice(df: pd.DataFrame, length: int) -> pd.Series:
    """(highest high + lowest low) / 2 over a trailing window of ``length`` bars."""
    highest = df[HIGH].rolling(length, min_periods=length).max()
    lowest = df[LOW].rolling(length, min_periods=length).min()
    return 0.5 * (highest + lowest)


def ichimoku(
    df: pd.DataFrame,
    tenkan: int = 9,
    kijun: int = 26,
    senkou: int = 52,
) -> dict:
    """Unshifted (causal) Ichimoku conversion/base lines and leading spans A/B.

    Spans are returned on the CURRENT bar (NOT forward-shifted) so the indicator never looks
    ahead; see the module docstring for the no-shift rationale.
    """
    tenkan_sen = _midprice(df, tenkan)
    kijun_sen = _midprice(df, kijun)
    span_a = 0.5 * (tenkan_sen + kijun_sen)
    span_b = _midprice(df, senkou)
    return {
        "tenkan": tenkan_sen,
        "kijun": kijun_sen,
        "span_a": span_a,
        "span_b": span_b,
    }


@INDICATORS.register
class Ichimoku(Indicator):
    """Ichimoku Kinko Hyo (Conversion/Base lines + Leading Spans A/B).

    What: four midprice lines (rolling high/low midpoints over 9/26/52 bars, plus the A/B
        leading spans) that together frame trend, support/resistance, and momentum at a glance.
    Best settings: 9 / 26 / 52 (Hosoda's originals on daily bars).
    Edge cases: each line warms up over its own window (tenkan 9, kijun/span_a 26, span_b 52);
        a flat window still yields a defined midprice (no division involved).
    Causality: spans are UNSHIFTED (causal=True). The classic chart leads them ``kijun`` bars
        into the future (look-ahead) — shift downstream if you want the visual cloud.
    Parity: pandas-ta ``ichimoku`` conversion/base directly; A/B compared against pandas-ta's
        pre-shift spans (its visible df forward-shifts them).
    """

    spec = IndicatorSpec(
        name="ichimoku",
        category="trend",
        aliases=("Ichimoku Kinko Hyo", "Ichimoku Cloud", "Kumo"),
        inputs=(HIGH, LOW),
        outputs=("tenkan", "kijun", "span_a", "span_b"),
        # Unshifted on purpose: forward-shifting the spans (the visual cloud) is look-ahead.
        causal=True,
        references=("Hosoda", "pandas-ta ichimoku", "ta IchimokuIndicator"),
        doc="ref/ta_docs/trend/Ichimoku.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        tenkan: int = Field(default=9, ge=1)
        kijun: int = Field(default=26, ge=1)
        senkou: int = Field(default=52, ge=1)

    def _compute(self, df: pd.DataFrame) -> dict:
        p = self.params
        return ichimoku(df, p["tenkan"], p["kijun"], p["senkou"])
