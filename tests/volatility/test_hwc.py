"""Holt-Winter Channel — golden + edge cases.

Golden values are captured directly from ``pandas_ta_classic.hwc`` (channel_eval=True) on a
fixed 10-bar close, so this file pins the exact recurrence even without the parity extra.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import frame
from pyindicators.core import CLOSE
from pyindicators.trend.hwma import hwma
from pyindicators.volatility.hwc import hwc  # noqa: F401  (import fires @register)

from pyindicators import INDICATORS  # isort: skip

_CLOSE = [10.0, 11.0, 10.5, 12.0, 13.0, 12.5, 11.0, 14.0, 15.0, 13.0]

# From pandas_ta_classic.hwc(close, na=.2, nb=.1, nc=.1, nd=.1, scalar=1, channel_eval=True).
_GOLD_MIDDLE = [
    10.000000, 10.221000, 10.305554, 10.711195, 11.289385,
    11.687283, 11.703335, 12.375211, 13.182933, 13.445270,
]
_GOLD_UPPER = [
    10.000000, 10.221000, 10.305554, 10.957536, 11.531039,
    12.154893, 12.402916, 13.086915, 13.893805, 14.293090,
]
_GOLD_LOWER = [
    10.000000, 10.221000, 10.305554, 10.464853, 11.047732,
    11.219674, 11.003755, 11.663507, 12.472062, 12.597450,
]


def test_golden_matches_reference_values():
    out = INDICATORS.create("hwc").compute(frame(_CLOSE))
    np.testing.assert_allclose(out["hwc_middle"].to_numpy(), _GOLD_MIDDLE, atol=1e-6)
    np.testing.assert_allclose(out["hwc_upper"].to_numpy(), _GOLD_UPPER, atol=1e-6)
    np.testing.assert_allclose(out["hwc_lower"].to_numpy(), _GOLD_LOWER, atol=1e-6)


def test_middle_equals_hwma_composition():
    # The centre line must be exactly the HWMA of close (no warm-up NaN, seeded at bar 0).
    df = frame(_CLOSE)
    out = INDICATORS.create("hwc").compute(df)
    np.testing.assert_allclose(out["hwc_middle"].to_numpy(), hwma(df[CLOSE]).to_numpy())


def test_width_and_pct_consistency():
    out = INDICATORS.create("hwc").compute(frame(_CLOSE))
    width = out["hwc_upper"] - out["hwc_lower"]
    np.testing.assert_allclose(out["hwc_width"].to_numpy(), width.to_numpy(), atol=1e-12)
    # pct = (close - lower) / width wherever the channel is open.
    c = pd.Series(_CLOSE)
    open_band = out["hwc_width"].to_numpy() > 0
    expected = ((c - out["hwc_lower"]) / out["hwc_width"]).to_numpy()
    np.testing.assert_allclose(
        out["hwc_pct"].to_numpy()[open_band], expected[open_band], atol=1e-9
    )


def test_first_two_bars_collapse_to_middle():
    # Variance has a one-bar lag and is seeded 0, so bars 0 and 1 have zero band width.
    out = INDICATORS.create("hwc").compute(frame(_CLOSE))
    for col in ("hwc_upper", "hwc_lower"):
        np.testing.assert_allclose(out[col].iloc[:2].to_numpy(), out["hwc_middle"].iloc[:2].to_numpy())
    assert (out["hwc_width"].iloc[:2] == 0.0).all()
    assert out["hwc_pct"].iloc[:2].isna().all()  # 0 / 0 guarded to NaN


def test_constant_series_flat_channel():
    # A perfectly flat close -> HWMA pinned at 7, band width is zero to floating-point noise.
    # The first 3 bars have *exactly* zero width (variance lag + seed) so pct is guarded to NaN;
    # afterwards HWMA accumulates ~1e-15 noise, giving the same -0.5 pct pandas-ta returns.
    out = INDICATORS.create("hwc").compute(frame([7.0] * 8))
    np.testing.assert_allclose(out["hwc_middle"].to_numpy(), 7.0)
    np.testing.assert_allclose(out["hwc_upper"].to_numpy(), 7.0)
    np.testing.assert_allclose(out["hwc_lower"].to_numpy(), 7.0)
    np.testing.assert_allclose(out["hwc_width"].to_numpy(), 0.0, atol=1e-12)
    assert out["hwc_pct"].iloc[:3].isna().all()  # exact-zero width -> 0/0 guarded


def test_scalar_scales_band_linearly():
    base = INDICATORS.create("hwc", scalar=1.0).compute(frame(_CLOSE))
    wide = INDICATORS.create("hwc", scalar=3.0).compute(frame(_CLOSE))
    # Middle is unchanged; the half-band scales exactly with `scalar`.
    np.testing.assert_allclose(base["hwc_middle"].to_numpy(), wide["hwc_middle"].to_numpy())
    base_half = (base["hwc_upper"] - base["hwc_middle"]).to_numpy()
    wide_half = (wide["hwc_upper"] - wide["hwc_middle"]).to_numpy()
    np.testing.assert_allclose(wide_half, 3.0 * base_half, atol=1e-9)


def test_single_row_frame_is_finite_and_flat():
    out = INDICATORS.create("hwc").compute(frame([42.0]))
    assert out.shape == (1, 5)
    np.testing.assert_allclose(out["hwc_middle"].to_numpy(), [42.0])
    np.testing.assert_allclose(out["hwc_upper"].to_numpy(), [42.0])
    np.testing.assert_allclose(out["hwc_lower"].to_numpy(), [42.0])


def test_output_contract():
    out = INDICATORS.create("hwc").compute(frame(_CLOSE))
    assert list(out.columns) == ["hwc_middle", "hwc_upper", "hwc_lower", "hwc_width", "hwc_pct"]
    assert (out.dtypes == np.float64).all()
    assert len(out) == len(_CLOSE)
