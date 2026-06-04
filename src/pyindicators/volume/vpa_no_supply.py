"""VPA No Supply — Volume Spread Analysis "No Supply" bar flag (Tom Williams / VSA).

A *No Supply* bar signals that sellers have withdrawn: price drifts down on a narrow spread
with volume drying up. Operationalised as a closed-form, per-bar boolean (0/1) over three
deterministic conditions, each measured against the **prior two bars only** (causal):

- **down close**  : ``close < close[-1]`` (the bar closes lower than the previous bar),
- **narrow spread**: ``(high - low) < (high - low)[-1]`` AND ``< (high - low)[-2]``
  (the bar's range is narrower than each of the two preceding ranges),
- **low volume**  : ``volume < volume[-1]`` AND ``< volume[-2]`` (volume below the prior two
  bars — supply, i.e. selling activity, is contracting).

When all three hold the bar is a No Supply bar (``1.0``), otherwise ``0.0``. The first two
bars have no two-bar history to compare against and are emitted as ``NaN`` (undefined, not
fabricated), matching the convention used by other look-back volume flags (e.g. ``pvr``).

Golden-only: no reference library (TA-Lib / pandas-ta / finta / ta / tulip) implements a VSA
No Supply primitive, so correctness is pinned by the explicit rule above and the closed-form
structural assertions in the tests, not by an external oracle.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import (
    CLOSE,
    HIGH,
    INDICATORS,
    LOW,
    VOLUME,
    Indicator,
    IndicatorSpec,
)


def vpa_no_supply(df: pd.DataFrame) -> pd.Series:
    """VSA No Supply flag: 1.0 on a narrow-range down-bar with volume below the prior 2 bars.

    All three conditions are evaluated against the two preceding bars only (strictly causal).
    The first two bars lack the required look-back and are returned as NaN.
    """
    spread = df[HIGH] - df[LOW]
    volume = df[VOLUME]

    down_close = df[CLOSE] < df[CLOSE].shift(1)
    narrow_spread = (spread < spread.shift(1)) & (spread < spread.shift(2))
    low_volume = (volume < volume.shift(1)) & (volume < volume.shift(2))

    flag = (down_close & narrow_spread & low_volume).astype("float64")
    # First two bars have no full two-bar look-back -> undefined.
    flag.iloc[:2] = np.nan
    return flag


@INDICATORS.register
class VpaNoSupply(Indicator):
    """VPA No Supply (Volume Spread Analysis).

    What: a 0/1 flag marking a "No Supply" bar — a narrow-range down close on volume below
        the prior two bars, i.e. selling pressure (supply) drying up.
    Best settings: none (per-bar; compares each bar to the two immediately preceding bars).
    Edge cases: first two bars have insufficient look-back -> NaN; ties (equal spread/volume)
        do not qualify because the comparisons are strict ``<``.
    Parity: golden-only (no reference-lib oracle); pinned by the explicit rule + closed-form
        structural tests.
    """

    spec = IndicatorSpec(
        name="vpa_no_supply",
        category="volume",
        aliases=("No Supply", "VSA No Supply", "Volume Spread Analysis No Supply"),
        inputs=(HIGH, LOW, CLOSE, VOLUME),
        outputs=("vpa_no_supply",),
        bounds={"vpa_no_supply": (0.0, 1.0)},
        references=("Tom Williams (VSA)", "golden-only (no reference-lib oracle)"),
        doc="ref/ta_docs/volume/misc_volume.md",
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return vpa_no_supply(df)
