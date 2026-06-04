"""VPA No Supply (VSA) — golden + edge cases.

Golden-only indicator: there is no reference-library oracle, so the rule is pinned here by
hand-built bars that exercise each branch (all three conditions met, and each one failing in
isolation), plus the warm-up / tie / bounds behaviour.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS

# Import the module directly so its @INDICATORS.register decorator fires under any test order.
from pyindicators.volume import vpa_no_supply as _mod  # noqa: F401


def _ns(high, low, close, volume):
    f = frame(close, high=high, low=low, volume=volume)
    return INDICATORS.create("vpa_no_supply").compute(f)["vpa_no_supply"]


def test_first_two_bars_are_nan():
    # No two-bar look-back exists for bars 0 and 1.
    out = _ns(
        high=[10.0, 10.0, 10.0, 10.0],
        low=[9.0, 9.0, 9.0, 9.0],
        close=[9.5, 9.5, 9.5, 9.5],
        volume=[100.0, 100.0, 100.0, 100.0],
    )
    assert np.isnan(out.iloc[0])
    assert np.isnan(out.iloc[1])
    assert np.isfinite(out.iloc[2])


def test_fires_on_no_supply_bar():
    # Bars 0,1 are wide-range / high-volume; bar 2 is a narrow-range down-bar on low volume:
    #   down close   : 9.0 < 9.5
    #   narrow spread: 0.2 < 1.0 (bar1) and 0.2 < 1.0 (bar0)
    #   low volume   : 50 < 300 and 50 < 200
    out = _ns(
        high=[10.0, 10.0, 9.10],
        low=[9.0, 9.0, 8.90],
        close=[9.5, 9.5, 9.00],
        volume=[200.0, 300.0, 50.0],
    )
    assert out.iloc[2] == 1.0


def test_up_close_does_not_fire():
    # Identical to the firing case but the close is UP (9.6 > 9.5) -> not a down bar.
    out = _ns(
        high=[10.0, 10.0, 9.10],
        low=[9.0, 9.0, 8.90],
        close=[9.5, 9.5, 9.60],
        volume=[200.0, 300.0, 50.0],
    )
    assert out.iloc[2] == 0.0


def test_wide_spread_does_not_fire():
    # Down close + low volume, but the spread (1.5) is wider than the prior bars (1.0).
    out = _ns(
        high=[10.0, 10.0, 9.75],
        low=[9.0, 9.0, 8.25],
        close=[9.5, 9.5, 9.00],
        volume=[200.0, 300.0, 50.0],
    )
    assert out.iloc[2] == 0.0


def test_high_volume_does_not_fire():
    # Down close + narrow spread, but volume (400) exceeds both prior bars.
    out = _ns(
        high=[10.0, 10.0, 9.10],
        low=[9.0, 9.0, 8.90],
        close=[9.5, 9.5, 9.00],
        volume=[200.0, 300.0, 400.0],
    )
    assert out.iloc[2] == 0.0


def test_volume_below_only_one_prior_bar_does_not_fire():
    # Volume (250) is below bar1 (300) but NOT below bar0 (200) -> low_volume requires BOTH.
    out = _ns(
        high=[10.0, 10.0, 9.10],
        low=[9.0, 9.0, 8.90],
        close=[9.5, 9.5, 9.00],
        volume=[200.0, 300.0, 250.0],
    )
    assert out.iloc[2] == 0.0


def test_strict_inequalities_on_ties():
    # Equal spread AND equal volume to the prior bars -> strict "<" means no fire,
    # even though the close ticks down.
    out = _ns(
        high=[10.0, 10.0, 10.0],
        low=[9.0, 9.0, 9.0],
        close=[9.6, 9.5, 9.0],
        volume=[100.0, 100.0, 100.0],
    )
    assert out.iloc[2] == 0.0


def test_output_is_binary_and_bounded_on_real_walk():
    out = INDICATORS.create("vpa_no_supply").compute(deterministic_frame(400))["vpa_no_supply"]
    vals = out.dropna().to_numpy()
    assert vals.size == 398  # 400 bars minus the 2-bar warm-up
    assert set(np.unique(vals)).issubset({0.0, 1.0})
    assert np.isfinite(out.iloc[-1])  # last row is a real flag, not warm-up NaN
    assert vals.sum() >= 1  # the pattern does occur somewhere on a 400-bar walk
