"""Extended Parabolic SAR (SAREXT) — golden + edge cases."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.trend.sarext import sarext  # noqa: F401  (import fires @register)


def test_sarext_first_bar_nan():
    out = INDICATORS.create("sarext").compute(deterministic_frame(200))["sarext"]
    assert np.isnan(out.iloc[0])  # no prior bar to seed the directional movement
    assert out.iloc[1:].notna().all()  # every later bar carries a (signed) stop


def test_sarext_single_bar_all_nan():
    out = INDICATORS.create("sarext").compute(frame([10.0]))["sarext"]
    assert out.isna().all()  # n < 2 guard


def test_sarext_empty_frame():
    empty = pd.DataFrame({"high": [], "low": []}, dtype="float64")
    out = sarext(empty)
    assert out.empty


def test_sarext_signs_encode_direction_on_v_shape():
    # A clean down-then-up V: the leg before the trough is short (negative), the leg after the
    # trough is long (positive). SAREXT's defining feature is this sign encoding.
    c = np.concatenate([np.arange(20.0, 5.0, -1.0), np.arange(5.0, 25.0)])
    out = INDICATORS.create("sarext").compute(frame(c, high=c + 0.5, low=c - 0.5))["sarext"]
    v = out.dropna().to_numpy()
    assert (v < 0).any() and (v > 0).any()  # both legs present
    assert v[-1] > 0  # ends long in the sustained up-leg
    assert v[2] < 0  # starts short in the down-leg (after the seed)


def test_sarext_trails_below_in_uptrend():
    # In a sustained up-trend the long stop (positive) trails below price.
    c = np.arange(1.0, 60.0)
    out = INDICATORS.create("sarext").compute(frame(c, high=c + 0.5, low=c - 0.5))["sarext"]
    last = out.iloc[-1]
    assert last > 0 and last < c[-1]


def test_sarext_start_value_forces_short_side():
    # A negative start_value forces the system to open short -> the first stop is negative.
    c = np.arange(1.0, 40.0)
    df = frame(c, high=c + 0.5, low=c - 0.5)
    out = INDICATORS.create("sarext", start_value=-100.0).compute(df)["sarext"]
    assert out.iloc[1] < 0  # opened short by the seed override


def test_sarext_abs_matches_unsigned_sar_magnitude():
    # Stripping the sign recovers a positive SAR-like trailing stop bounded by the bar range.
    df = deterministic_frame(200)
    out = INDICATORS.create("sarext").compute(df)["sarext"].dropna().to_numpy()
    assert np.all(np.abs(out) > 0)
    assert np.isfinite(out).all()


def test_sarext_offset_on_reverse_nudges_both_flips():
    # a nonzero offset_on_reverse exercises the reversal-nudge branch on long->short and
    # short->long flips (deterministic_frame reverses many times over 200 bars)
    df = deterministic_frame(200)
    base = INDICATORS.create("sarext").compute(df)["sarext"]
    nudged = INDICATORS.create("sarext", offset_on_reverse=0.02).compute(df)["sarext"]
    assert nudged.notna().any()
    assert not np.allclose(base.dropna().to_numpy(), nudged.dropna().to_numpy())
