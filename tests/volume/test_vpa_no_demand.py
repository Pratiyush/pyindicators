"""VPA No Demand — golden (handcrafted, every branch) + edge cases.

Import the module directly so the ``@INDICATORS.register`` decorator fires even when this
file is run in isolation.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.volume.vpa_no_demand import vpa_no_demand  # noqa: F401  (registers)

NAME = "vpa_no_demand"


def _golden_frame():
    """Bars engineered to hit each branch of the rule (spread == high - low).

    i  close  spread  volume  expected  why
    0  100    5       1000    NaN       warm-up (no prior pair)
    1  101    5       1000    NaN       warm-up (no prior pair)
    2  102    3        800    1         up; spread<both priors; vol<both priors
    3  101    2        700    0         down close -> not an up bar
    4  103    1        600    1         up; spread<both priors; vol<both priors
    5  104    4        500    0         up & low vol but spread NOT narrower than prior
    6  105    0.5      900    0         up & narrow but vol NOT below prior two
    """
    close = [100.0, 101.0, 102.0, 101.0, 103.0, 104.0, 105.0]
    spread = [5.0, 5.0, 3.0, 2.0, 1.0, 4.0, 0.5]
    low = [50.0] * len(close)
    high = [lo + sp for lo, sp in zip(low, spread, strict=True)]
    volume = [1000.0, 1000.0, 800.0, 700.0, 600.0, 500.0, 900.0]
    return frame(close, high=high, low=low, volume=volume)


def test_golden_exact_flags():
    out = INDICATORS.create(NAME).compute(_golden_frame())[NAME]
    assert np.isnan(out.iloc[0]) and np.isnan(out.iloc[1])  # two-bar warm-up
    np.testing.assert_array_equal(
        out.iloc[2:].to_numpy(),
        np.array([1.0, 0.0, 1.0, 0.0, 0.0]),
    )


def test_function_matches_indicator():
    df = _golden_frame()
    a = vpa_no_demand(df)
    b = INDICATORS.create(NAME).compute(df)[NAME]
    np.testing.assert_array_equal(a.fillna(-1).to_numpy(), b.fillna(-1).to_numpy())


def test_only_zero_one_and_nan():
    out = INDICATORS.create(NAME).compute(deterministic_frame(300))[NAME]
    finite = out.dropna().to_numpy()
    assert set(np.unique(finite)).issubset({0.0, 1.0})
    assert finite.size > 0  # the signal does fire / not-fire across a real walk


def test_warmup_is_nan_only_first_two_bars():
    out = INDICATORS.create(NAME).compute(deterministic_frame(50))[NAME]
    assert np.isnan(out.iloc[0]) and np.isnan(out.iloc[1])
    assert out.iloc[2:].notna().all()  # everything after warm-up is defined


def test_equal_spread_or_volume_does_not_trigger():
    # Strict "<" : a tie on spread OR on volume must NOT qualify as No Demand.
    close = [100.0, 101.0, 102.0]
    spread = [3.0, 3.0, 3.0]  # spread tie with prior bars -> narrow is False
    low = [50.0, 50.0, 50.0]
    high = [lo + sp for lo, sp in zip(low, spread, strict=True)]
    volume = [900.0, 900.0, 100.0]  # volume clearly low, but spread tie blocks the signal
    out = vpa_no_demand(frame(close, high=high, low=low, volume=volume))
    assert out.iloc[2] == 0.0


def test_nan_input_propagates_not_crashes():
    df = deterministic_frame(40)
    df.loc[df.index[20], "high"] = np.nan  # corrupt one bar's spread
    out = INDICATORS.create(NAME).compute(df)[NAME]
    assert len(out) == len(df)
    assert np.isnan(out.iloc[20])  # corrupted bar is undefined
    # The bar two steps later reads bar 20 as a prior -> also undefined.
    assert np.isnan(out.iloc[21]) and np.isnan(out.iloc[22])


def test_causal_truncation_invariance():
    # Value at bar i must not change when later bars are removed.
    df = deterministic_frame(120)
    full = INDICATORS.create(NAME).compute(df)[NAME]
    trunc = INDICATORS.create(NAME).compute(df.iloc[:60].copy())[NAME]
    np.testing.assert_array_equal(
        full.iloc[:60].fillna(-1).to_numpy(), trunc.fillna(-1).to_numpy()
    )
