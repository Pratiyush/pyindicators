"""HWC — Holt-Winter Channel (volatility envelope around an HWMA middle).

A channel built on the Holt-Winter Moving Average: the centre line is exactly HWMA (triple
smoothing of level/velocity/acceleration), and the bands sit at ``+/- scalar * stddev`` where
``stddev`` is the square root of an exponentially-smoothed variance of the *previous* bar's
``(price - HWMA)`` error. Ported for MetaTrader 5 and pandas-ta by rengel8, extended with a
channel width and a percent price-position-within-channel. Composes ``trend.hwma`` for the
middle line. See ``ref/ta_docs/volatility/misc_volatility.md``.

1. What: an HWMA centre line with a self-adapting volatility channel + width/position extras.
2. Inputs: close.
3. Params: na/nb/nc (HWMA level/velocity/accel weights, each in (0,1)); nd (variance smoothing,
   in (0,1)); scalar (band multiplier, > 0).
4. Outputs: hwc_middle, hwc_upper, hwc_lower, hwc_width, hwc_pct.
5. Formula: middle = HWMA(close, na, nb, nc); var[i] = (1-nd)*var[i-1] + nd*(c[i-1]-mid[i-1])^2
   (seeded 0); stddev[i] = sqrt(var[i-1]); upper/lower = middle +/- scalar*stddev;
   width = upper - lower; pct = (close - lower) / width.
6. Edge cases: bars 0-1 have stddev 0 (channel collapses to the middle until variance warms up),
   so ``pct`` there is 0/0 guarded to NaN; on a flat series the HWMA recurrence accrues ~1e-15
   noise after warm-up, matching pandas-ta's near-zero width and -0.5 pct exactly.
7. Causal: yes (every value at bar i depends only on rows <= i).
8. Stateful: yes (variance and HWMA are path-dependent recurrences).
9. Bounds: none.
10. Parity: pandas_ta_classic ``hwc`` (channel_eval=True), exact across all five columns.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.core import CLOSE, INDICATORS, Indicator, IndicatorSpec, safe_divide
from pyindicators.trend.hwma import hwma


def hwc(
    close: pd.Series,
    na: float = 0.2,
    nb: float = 0.1,
    nc: float = 0.1,
    nd: float = 0.1,
    scalar: float = 1.0,
) -> dict[str, pd.Series]:
    """Holt-Winter Channel: HWMA middle plus a smoothed-variance band, width and %position."""
    middle = hwma(close, na, nb, nc)
    c_arr = close.to_numpy(dtype="float64")
    mid_arr = middle.to_numpy(dtype="float64")
    m = c_arr.size

    stddev = np.zeros(m, dtype="float64")
    last_var = 0.0
    # Seeds mirror pandas-ta: at bar 0 the lagged (price, mid) pair is (c[0], c[0]) -> err 0.
    last_price = c_arr[0] if m else 0.0
    last_mid = c_arr[0] if m else 0.0
    for i in range(m):
        stddev[i] = last_var**0.5  # uses the PREVIOUS bar's variance (one-bar lag)
        err = last_price - last_mid
        last_var = (1.0 - nd) * last_var + nd * err * err
        last_price = c_arr[i]
        last_mid = mid_arr[i]

    band = scalar * pd.Series(stddev, index=close.index)
    upper = middle + band
    lower = middle - band
    width = upper - lower
    pct = safe_divide(close - lower, width)  # NaN where the channel collapses (width == 0)
    return {
        "hwc_middle": middle,
        "hwc_upper": upper,
        "hwc_lower": lower,
        "hwc_width": width,
        "hwc_pct": pct,
    }


@INDICATORS.register
class HoltWinterChannel(Indicator):
    """Holt-Winter Channel.

    What: an HWMA centre line wrapped in a self-adapting volatility channel, plus the channel
        width and the percent position of price within the channel.
    Best settings: na 0.2, nb 0.1, nc 0.1, nd 0.1, scalar 1.0 (the MetaTrader/pandas-ta defaults).
    Edge cases: stddev is 0 for the first two bars (channel collapses to the middle while variance
        warms up), so ``hwc_pct`` is guarded to NaN there; a flat series keeps the band width within
        floating-point noise of zero (matching pandas-ta's -0.5 pct exactly).
    Parity: pandas_ta_classic ``hwc`` (channel_eval=True), exact across all five columns.
    """

    spec = IndicatorSpec(
        name="hwc",
        category="volatility",
        aliases=("Holt-Winter Channel",),
        inputs=(CLOSE,),
        outputs=("hwc_middle", "hwc_upper", "hwc_lower", "hwc_width", "hwc_pct"),
        stateful=True,
        references=("Holt-Winter", "pandas-ta hwc"),
        doc="ref/ta_docs/volatility/misc_volatility.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        na: float = Field(default=0.2, gt=0.0, lt=1.0)
        nb: float = Field(default=0.1, gt=0.0, lt=1.0)
        nc: float = Field(default=0.1, gt=0.0, lt=1.0)
        nd: float = Field(default=0.1, gt=0.0, lt=1.0)
        scalar: float = Field(default=1.0, gt=0.0)

    def _compute(self, df: pd.DataFrame) -> dict[str, pd.Series]:
        p = self.params
        return hwc(df[CLOSE], p["na"], p["nb"], p["nc"], p["nd"], p["scalar"])
