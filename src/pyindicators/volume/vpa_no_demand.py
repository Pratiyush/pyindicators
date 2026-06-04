"""VPA No Demand — Volume Spread Analysis "No Demand" bar (Tom Williams / VSA).

A *No Demand* bar is a textbook Volume Spread Analysis signal of absent professional
buying behind an up-move: the market closes up but on a **narrow spread** and on **low
volume** relative to the immediately preceding bars. The lack of effort (volume) behind
the upward result (up close) warns that the rise is unsupported and prone to fail.

This is a structural, golden-only indicator: no reference library (TA-Lib, pandas-ta,
finta, ta) ships a VSA No Demand function, so there is no oracle to match. The rule is
pinned here as a closed form and verified structurally (see the test files). Output is a
binary flag in {0, 1}; the two-bar warm-up (no prior pair to compare against) is NaN.

Rule (all three must hold on bar ``i``, with ``spread = high - low``):
  * up close   : ``close[i]  > close[i-1]``
  * narrow spread : ``spread[i] < spread[i-1]`` and ``spread[i] < spread[i-2]``
  * low volume : ``volume[i] < volume[i-1]`` and ``volume[i] < volume[i-2]``

Every comparison looks only backward, so the signal is strictly causal.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pyindicators.core import CLOSE, HIGH, INDICATORS, LOW, VOLUME, Indicator, IndicatorSpec


def vpa_no_demand(df: pd.DataFrame) -> pd.Series:
    """VSA No Demand flag: 1 on a narrow-range, low-volume up-bar, else 0.

    A bar qualifies when its close is up versus the prior close, its spread
    (``high - low``) is narrower than each of the prior two bars, and its volume is
    below each of the prior two bars. The first two bars are NaN (the spread/volume
    comparisons need two prior bars); any NaN input propagates to a NaN bar.
    """
    spread = df[HIGH] - df[LOW]
    volume = df[VOLUME]
    close = df[CLOSE]

    up_close = close > close.shift(1)
    narrow = (spread < spread.shift(1)) & (spread < spread.shift(2))
    low_volume = (volume < volume.shift(1)) & (volume < volume.shift(2))

    hit = up_close & narrow & low_volume
    out = pd.Series(np.where(hit, 1.0, 0.0), index=df.index)

    # Warm-up: bars 0 and 1 lack the two prior bars the spread/volume tests need; mark
    # them undefined rather than fabricating a 0. NaN inputs also make the bar undefined.
    out.iloc[:2] = np.nan
    inputs_nan = spread.isna() | volume.isna() | close.isna()
    prior_nan = (
        close.shift(1).isna()
        | spread.shift(1).isna()
        | spread.shift(2).isna()
        | volume.shift(1).isna()
        | volume.shift(2).isna()
    )
    return out.mask(inputs_nan | prior_nan)


@INDICATORS.register
class VPANoDemand(Indicator):
    """VPA No Demand bar.

    What: a Volume Spread Analysis flag for an up-close bar on a narrow spread and below
        the prior two bars' volume — a sign that no demand (professional buying) backs the
        rise, so it is liable to stall or reverse.
    Best settings: parameterless; the comparison window is the fixed prior two bars (VSA
        convention). Use on the timeframe you trade; pair with trend context.
    Edge cases: first two bars are NaN (no prior pair to compare); a NaN-laden bar (or a
        NaN in either of the two prior bars) propagates to NaN; otherwise strictly 0/1.
    Parity: golden-only — no reference library implements VSA No Demand. The closed-form
        rule above is verified structurally (handcrafted bars + invariants in the tests).
    """

    spec = IndicatorSpec(
        name="vpa_no_demand",
        category="volume",
        aliases=("No Demand", "VSA No Demand", "VPA No Demand"),
        inputs=(HIGH, LOW, CLOSE, VOLUME),
        outputs=("vpa_no_demand",),
        bounds={"vpa_no_demand": (0.0, 1.0)},
        references=("Tom Williams VSA", "Gavin Holmes Trading in the Shadow of the Smart Money"),
    )

    def _compute(self, df: pd.DataFrame) -> pd.Series:
        return vpa_no_demand(df)
