"""VPA Effort vs Result (VSA anomaly flag) — golden + edge cases.

Golden-only indicator: there is no reference-library oracle for Volume-Spread-Analysis, so the
exact closed-form rule is pinned here (and structurally re-checked in the parity file).
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS

# import the module directly so the @INDICATORS.register decorator fires
from pyindicators.volume.vpa_effort_vs_result import vpa_effort_vs_result  # noqa: F401


def _make(length=3):
    """A frame whose averages are easy to reason about.

    Bars 0..2 establish a baseline: spread 2.0 (10..12) and volume 100. Bar 3 is the anomaly
    bar — 5x volume but spread 0.5 — and its close location is set per-test via high/low/close.
    """
    high = [12.0, 12.0, 12.0, 11.5]
    low = [10.0, 10.0, 10.0, 11.0]
    close = [11.0, 11.0, 11.0, 11.4]  # near the top of the narrow bar 3 -> mfm > 0
    volume = [100.0, 100.0, 100.0, 500.0]
    return frame(close, high=high, low=low, volume=volume), length


def test_bullish_anomaly_high_effort_small_result_close_high():
    f, length = _make()
    out = INDICATORS.create(
        "vpa_effort_vs_result", length=length, effort_mult=2.0, result_mult=0.7
    ).compute(f)["vpa_effort_vs_result"]
    # bars 0..2: warm-up / no anomaly -> 0; bar 3: effort 5x, spread 0.25x, close high -> +1
    assert out.tolist() == [0.0, 0.0, 0.0, 1.0]


def test_bearish_anomaly_close_low_flips_sign():
    high = [12.0, 12.0, 12.0, 11.5]
    low = [10.0, 10.0, 10.0, 11.0]
    close = [11.0, 11.0, 11.0, 11.1]  # near the bottom of the narrow bar 3 -> mfm < 0
    volume = [100.0, 100.0, 100.0, 500.0]
    f = frame(close, high=high, low=low, volume=volume)
    out = INDICATORS.create("vpa_effort_vs_result", length=3).compute(f)["vpa_effort_vs_result"]
    assert out.iloc[3] == -1.0


def test_high_volume_but_wide_spread_is_not_an_anomaly():
    # Big volume AND a big spread = effort produced a result -> no flag (result > result_mult).
    high = [12.0, 12.0, 12.0, 16.0]
    low = [10.0, 10.0, 10.0, 8.0]  # spread 8.0 = 4x baseline
    close = [11.0, 11.0, 11.0, 15.5]
    volume = [100.0, 100.0, 100.0, 500.0]
    f = frame(close, high=high, low=low, volume=volume)
    out = INDICATORS.create("vpa_effort_vs_result", length=3).compute(f)["vpa_effort_vs_result"]
    assert out.iloc[3] == 0.0


def test_small_spread_but_normal_volume_is_not_an_anomaly():
    # Narrow bar but only average volume = no effort -> no flag (effort < effort_mult).
    high = [12.0, 12.0, 12.0, 11.5]
    low = [10.0, 10.0, 10.0, 11.0]
    close = [11.0, 11.0, 11.0, 11.4]
    volume = [100.0, 100.0, 100.0, 100.0]
    f = frame(close, high=high, low=low, volume=volume)
    out = INDICATORS.create("vpa_effort_vs_result", length=3).compute(f)["vpa_effort_vs_result"]
    assert out.iloc[3] == 0.0


def test_thresholds_are_inclusive():
    # The comparisons are >= / <=, so a bar landing *exactly* on both thresholds must still flag.
    # We avoid FP-boundary guesswork by reading back the bar's true effort/result ratios and
    # using them verbatim as the thresholds, then asserting the flag fires.
    high = [12.0, 12.0, 12.0, 12.0]
    low = [10.0, 10.0, 10.0, 11.0]  # narrow bar 3
    close = [11.0, 11.0, 11.0, 11.9]  # close high -> +1
    volume = [100.0, 100.0, 100.0, 260.0]
    f = frame(close, high=high, low=low, volume=volume)

    spread = f["high"] - f["low"]
    effort_at_3 = (f["volume"] / f["volume"].rolling(3).mean()).iloc[3]
    result_at_3 = (spread / spread.rolling(3).mean()).iloc[3]

    out = INDICATORS.create(
        "vpa_effort_vs_result", length=3, effort_mult=effort_at_3, result_mult=result_at_3
    ).compute(f)["vpa_effort_vs_result"]
    assert out.iloc[3] == 1.0  # exactly-on-threshold bar is included

    # And nudging both thresholds just past the bar's ratios drops the flag (strict exclusion).
    out2 = INDICATORS.create(
        "vpa_effort_vs_result",
        length=3,
        effort_mult=effort_at_3 * 1.0001,
        result_mult=result_at_3 * 0.9999,
    ).compute(f)["vpa_effort_vs_result"]
    assert out2.iloc[3] == 0.0


def test_zero_spread_bar_never_flagged():
    # high == low on the candidate bar: spread 0 -> result 0 and mfm 0 -> no direction -> 0.
    high = [12.0, 12.0, 12.0, 11.0]
    low = [10.0, 10.0, 10.0, 11.0]  # high == low == close
    close = [11.0, 11.0, 11.0, 11.0]
    volume = [100.0, 100.0, 100.0, 500.0]
    f = frame(close, high=high, low=low, volume=volume)
    out = INDICATORS.create("vpa_effort_vs_result", length=3).compute(f)["vpa_effort_vs_result"]
    assert out.iloc[3] == 0.0


def test_output_is_strictly_signed_and_bounded():
    out = INDICATORS.create("vpa_effort_vs_result").compute(deterministic_frame(300))[
        "vpa_effort_vs_result"
    ]
    vals = set(np.unique(out.dropna().to_numpy()).tolist())
    assert vals.issubset({-1.0, 0.0, 1.0})
    assert out.min() >= -1.0 and out.max() <= 1.0


def test_no_nan_emitted_even_during_warmup():
    # The flag is a decision (0 = "no anomaly"), so it is defined on every bar, including warm-up.
    out = INDICATORS.create("vpa_effort_vs_result", length=20).compute(deterministic_frame(100))[
        "vpa_effort_vs_result"
    ]
    assert not out.isna().any()
