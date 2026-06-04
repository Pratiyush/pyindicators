"""VPA Effort vs Result — Volume-Spread-Analysis (VSA) anomaly flag (Wyckoff / Tom Williams).

VSA reads each bar as *effort* (volume) against *result* (price spread, high-low). The classic
anomaly is **high effort but small result**: a bar trades far more volume than normal yet barely
moves — selling absorbed by buying (or vice-versa), i.e. the smart-money "no result for the
effort" tell. We emit a *signed* flag so the divergence carries direction:

* ``+1`` bullish anomaly: effort high, result small, close in the **upper** half of the bar
  (demand absorbing supply — accumulation),
* ``-1`` bearish anomaly: effort high, result small, close in the **lower** half of the bar
  (supply absorbing demand — distribution),
* ``0`` no effort/result anomaly (the overwhelming majority of bars).

Effort and result are each measured *relative to their own trailing ``length``-bar SMA* (so the
flag is scale-free and self-calibrating), composing :func:`base.sma`. Close location uses the
Accumulation/Distribution Money-Flow-Multiplier convention ``((C-L)-(H-C))/(H-L)`` so the sign
agrees with :mod:`pyindicators.volume.ad`. Golden-only: no reference library implements VSA, so
the exact rule below is the contract and is asserted by closed-form tests. See
``ref/ta_docs/volume/misc_volume.md``.
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


def vpa_effort_vs_result(
    df: pd.DataFrame,
    length: int = 20,
    effort_mult: float = 2.0,
    result_mult: float = 0.7,
) -> pd.Series:
    """Signed VSA effort-vs-result anomaly flag in ``{-1, 0, +1}``.

    Rule (all comparisons are bar-local, using trailing ``length`` averages — fully causal):

    * ``effort  = volume / SMA(volume, length)``  (a.k.a. relative volume),
    * ``result  = (high - low) / SMA(high - low, length)``  (relative spread),
    * ``mfm     = ((close - low) - (high - close)) / (high - low)``  (close location, -1..+1),
    * ``anomaly = (effort >= effort_mult) & (result <= result_mult)``,
    * output ``+1`` where ``anomaly & mfm > 0``, ``-1`` where ``anomaly & mfm < 0``, else ``0``.

    Edge handling: a zero-spread bar (high == low) -> ``mfm`` 0 (via ``safe_divide`` fill) and
    ``result`` 0, so it can never be flagged (no result *and* no direction). During the
    ``length-1``-bar warm-up the SMAs are NaN, the comparisons are False, and the flag is ``0``
    ("no anomaly"); any NaN tick likewise yields ``0`` rather than crashing.
    """
    spread = df[HIGH] - df[LOW]
    effort = safe_divide(df[VOLUME], sma(df[VOLUME], length))
    result = safe_divide(spread, sma(spread, length))
    mfm = safe_divide((df[CLOSE] - df[LOW]) - (df[HIGH] - df[CLOSE]), spread, fill=0.0)

    anomaly = (effort >= effort_mult) & (result <= result_mult)
    signal = np.where(anomaly & (mfm > 0.0), 1.0, np.where(anomaly & (mfm < 0.0), -1.0, 0.0))
    return pd.Series(signal, index=df.index)


@INDICATORS.register
class VPAEffortVsResult(Indicator):
    """VPA Effort vs Result.

    What: a signed VSA anomaly flag — high volume (effort) on a small price spread (result) is
        absorption; the sign (close in the upper/lower half of the bar) reads it as
        accumulation (+1) or distribution (-1).
    Best settings: ``length`` 20-30; ``effort_mult`` ~2 (volume >= 2x average) and
        ``result_mult`` ~0.7 (spread <= 0.7x average) for a high-conviction "no result" bar.
    Edge cases: high==low bar can't be flagged (no spread, no direction); warm-up and NaN ticks
        yield 0; output is exactly -1/0/+1.
    Parity: golden-only (no library implements VSA) — the closed-form rule is asserted directly.
    """

    spec = IndicatorSpec(
        name="vpa_effort_vs_result",
        category="volume",
        aliases=("VSA Effort vs Result", "Volume Spread Analysis Anomaly"),
        inputs=(HIGH, LOW, CLOSE, VOLUME),
        outputs=("vpa_effort_vs_result",),
        bounds={"vpa_effort_vs_result": (-1.0, 1.0)},
        references=("Wyckoff", "Tom Williams (VSA)"),
        doc="ref/ta_docs/volume/misc_volume.md",
    )

    class Params(BaseModel):
        model_config = ConfigDict(extra="forbid", frozen=True)
        length: int = Field(default=20, ge=1)
        effort_mult: float = Field(default=2.0, gt=0)
        result_mult: float = Field(default=0.7, gt=0)

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return vpa_effort_vs_result(
            df,
            self.params["length"],
            self.params["effort_mult"],
            self.params["result_mult"],
        )
