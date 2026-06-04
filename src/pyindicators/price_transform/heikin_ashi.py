"""Heikin-Ashi — smoothed candles (price transform).

``HA_Close = (O+H+L+C)/4``; ``HA_Open_t = (HA_Open_{t-1} + HA_Close_{t-1})/2`` (seeded with
``(O_0+C_0)/2``); ``HA_High = max(H, HA_Open, HA_Close)``; ``HA_Low = min(L, HA_Open,
HA_Close)``. HA_Open is recursive (stateful). See ``ref/ta_docs/price_transform/price_transforms.md``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, OPEN, Indicator, IndicatorSpec


def heikin_ashi(df: pd.DataFrame) -> dict:
    """Heikin-Ashi open/high/low/close (smoothed candles)."""
    o = df[OPEN].to_numpy(dtype="float64")
    h = df[HIGH].to_numpy(dtype="float64")
    low_arr = df[LOW].to_numpy(dtype="float64")
    c = df[CLOSE].to_numpy(dtype="float64")
    n = c.size
    ha_close = (o + h + low_arr + c) / 4.0
    ha_open = np.empty(n, dtype="float64")
    for i in range(n):
        if i == 0:
            ha_open[i] = (o[0] + c[0]) / 2.0  # seed: (open0 + close0)/2
        else:
            ha_open[i] = (ha_open[i - 1] + ha_close[i - 1]) / 2.0
    ha_high = np.maximum.reduce([h, ha_open, ha_close])
    ha_low = np.minimum.reduce([low_arr, ha_open, ha_close])
    idx = df.index
    return {
        "ha_open": pd.Series(ha_open, index=idx),
        "ha_high": pd.Series(ha_high, index=idx),
        "ha_low": pd.Series(ha_low, index=idx),
        "ha_close": pd.Series(ha_close, index=idx),
    }


@INDICATORS.register
class HeikinAshi(Indicator):
    """Heikin-Ashi.

    What: smoothed candles that filter noise; consecutive same-colour candles = trend persistence.
    Best settings: none (per-bar transform with a recursive open).
    Edge cases: HA_Open is recursive and explicitly seeded at bar 0 (no NaN warm-up).
    Parity: pandas-ta ``ha`` (not in core TA-Lib).
    """

    spec = IndicatorSpec(
        name="heikin_ashi",
        category="price_transform",
        aliases=("Heikin-Ashi", "HA"),
        inputs=(OPEN, HIGH, LOW, CLOSE),
        outputs=("ha_open", "ha_high", "ha_low", "ha_close"),
        stateful=True,
        references=("pandas-ta ha", "finta HEIKIN_ASHI"),
        doc="ref/ta_docs/price_transform/price_transforms.md",
    )

    def _compute(self, df: pd.DataFrame) -> dict:
        return heikin_ashi(df)
