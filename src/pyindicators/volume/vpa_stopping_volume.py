"""VPA Stopping Volume — Volume Spread Analysis "stopping volume" signal (0/1 flag).

Stopping Volume (Tom Williams / Wyckoff VSA) is the footprint of *demand absorbing supply* at
the end of a fall: after a downtrend, a *down-bar* prints on **unusually high volume** yet
**closes well off its low** (a long lower shadow). The wide spread + heavy volume show heavy
selling, but the close back up near the high shows that buying stepped in and "stopped" the
decline — a potential bottoming signal.

There is no canonical oracle for this pattern (no TA-Lib / pandas-ta / finta / ta function),
so this is a **golden-only, structural** indicator: every condition is a deterministic
inequality and the output is a strict 0/1 flag. The four conditions evaluated on bar ``i`` are:

1. Downtrend context: ``close[i] < SMA(close, trend_length)[i]``  (price below its trend mean).
2. Down-bar:          ``close[i] < close[i-1]``                     (closes below the prior close).
3. High volume:       ``volume[i] > vol_mult * SMA(volume, vol_length)[i]``  (above-average effort).
4. Close off the low: ``(close[i] - low[i]) / (high[i] - low[i]) >= close_loc``  (long lower shadow).

All inputs are at or before bar ``i`` (trailing SMAs + the previous close), so the signal is
**causal** — no look-ahead. The volume baseline reuses ``base.sma`` on volume (the same
"normal volume" baseline RVOL/Volume-SMA use). Division for the close location is guarded with
``safe_divide`` (a zero-range doji -> NaN -> condition False). During warm-up (before either SMA
window fills) the flag is **0**, never NaN, matching the convention used by the candlestick
patterns (a pattern that cannot be evaluated has not fired). Bounded to ``{0, 1}`` ⊂ [0, 1].
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from pyindicators.base import sma
from pyindicators.core import (
    CLOSE,
    HIGH,
    INDICATORS,
    LOW,
    VOLUME,
    Indicator,
    IndicatorSpec,
    safe_divide,
)


def vpa_stopping_volume(
    df: pd.DataFrame,
    trend_length: int = 20,
    vol_length: int = 20,
    vol_mult: float = 1.5,
    close_loc: float = 0.5,
) -> pd.Series:
    """VSA Stopping Volume flag (1.0 where the pattern fires, else 0.0).

    A bar flags when, after a downtrend (close below its ``trend_length`` SMA), a down-bar
    (close below the prior close) prints on high volume (above ``vol_mult`` x the
    ``vol_length`` volume SMA) yet closes in the upper ``(1 - close_loc)`` of its range
    (a long lower shadow). Warm-up bars (before the SMAs fill) are 0, not NaN.
    """
    close = df[CLOSE]
    high = df[HIGH]
    low = df[LOW]
    volume = df[VOLUME]

    downtrend = close < sma(close, trend_length)
    down_bar = close < close.shift(1)
    high_volume = volume > vol_mult * sma(volume, vol_length)
    # Where in the bar's range the close sits: 1.0 = closes at the high, 0.0 = at the low.
    # A zero-range bar (high == low) -> safe_divide NaN -> comparison False (cannot judge a wick).
    close_location = safe_divide(close - low, high - low)
    off_the_low = close_location >= close_loc

    # NaN from any warm-up SMA makes its boolean column False, so the AND is False -> 0.0.
    hit = downtrend & down_bar & high_volume & off_the_low
    return pd.Series(np.where(hit.to_numpy(), 1.0, 0.0), index=df.index)


@INDICATORS.register
class VPAStoppingVolume(Indicator):
    """VPA Stopping Volume (VSA).

    What: a 0/1 flag for Volume-Spread-Analysis "stopping volume" — a high-volume down-bar
    that closes well off its low (long lower shadow) after a downtrend, signalling demand
    absorbing supply (a potential bottom).
    Best settings: ``trend_length``/``vol_length`` 20, ``vol_mult`` 1.5 (high effort),
    ``close_loc`` 0.5 (close in the upper half of the range). Raise ``vol_mult``/``close_loc``
    for a stricter signal.
    Edge cases: warm-up bars are 0 (not NaN); a zero-range bar can never close "off its low"
    (guarded division -> False); output is strictly 0 or 1.
    Parity: golden-only — no reference library implements stopping volume; validated against
    the closed-form four-condition definition (see ``tests/parity/test_parity_vpa_stopping_volume.py``).
    """

    spec = IndicatorSpec(
        name="vpa_stopping_volume",
        category="volume",
        aliases=("Stopping Volume", "VSA Stopping Volume"),
        inputs=(HIGH, LOW, CLOSE, VOLUME),
        outputs=("vpa_stopping_volume",),
        bounds={"vpa_stopping_volume": (0.0, 1.0)},
        references=("Tom Williams (VSA)", "Wyckoff"),
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        trend_length: int = Field(default=20, ge=1)
        vol_length: int = Field(default=20, ge=1)
        vol_mult: float = Field(default=1.5, gt=0)
        close_loc: float = Field(default=0.5, ge=0.0, le=1.0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return vpa_stopping_volume(
            df,
            self.params["trend_length"],
            self.params["vol_length"],
            self.params["vol_mult"],
            self.params["close_loc"],
        )
