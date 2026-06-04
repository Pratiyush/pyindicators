"""Three Outside Up/Down — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.three_outside import three_outside  # noqa: F401  (fires @register)


def _three(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("three_outside").compute(df)["three_outside"].to_numpy()


def test_three_outside_up_strict():
    # bar1 black (100->99), bar2 white (98->101) strictly engulfs, bar3 closes higher -> +100.
    out = _three(
        [100.0, 100.0, 98.0, 101.0],
        [100.0, 100.0, 101.5, 102.5],
        [100.0, 98.5, 97.5, 100.5],
        [100.0, 99.0, 101.0, 102.0],
    )
    assert out[3] == 100.0


def test_three_outside_down_strict():
    # bar1 white (100->101), bar2 black (102->99) strictly engulfs, bar3 closes lower -> -100.
    out = _three(
        [100.0, 100.0, 102.0, 99.0],
        [100.0, 101.5, 102.5, 99.5],
        [100.0, 99.5, 98.5, 97.5],
        [100.0, 101.0, 99.0, 98.0],
    )
    assert out[3] == -100.0


def test_three_outside_up_needs_higher_close():
    # Valid bullish engulfing on bars 1-2 but bar3 fails to close above bar2's close -> 0.
    out = _three(
        [100.0, 100.0, 98.0, 100.5],
        [100.0, 100.0, 101.5, 101.5],
        [100.0, 98.5, 97.5, 100.0],
        [100.0, 99.0, 101.0, 101.0],  # bar3 close 101.0 == bar2 close 101.0, not strictly above
    )
    assert out[3] == 0.0


def test_three_outside_touching_edge_is_zero():
    # Engulfing edge merely touches (bar2 open == bar1 close): strict test fails -> 0
    # (no ±80 partial score, unlike CDLENGULFING).
    out = _three(
        [100.0, 100.0, 99.0, 101.0],
        [100.0, 100.0, 101.5, 102.5],
        [100.0, 98.5, 98.5, 100.5],
        [100.0, 99.0, 101.0, 102.0],  # bar2 open 99.0 == bar1 close 99.0 -> touch, not strict
    )
    assert out[3] == 0.0


def test_three_outside_lookback_zeros_first_three():
    out = _three(
        [100.0, 100.0, 98.0, 101.0],
        [100.0, 100.0, 101.5, 102.5],
        [100.0, 98.5, 97.5, 100.5],
        [100.0, 99.0, 101.0, 102.0],
    )
    np.testing.assert_array_equal(out[:3], 0.0)  # TA-Lib lookback = 3


def test_three_outside_short_frame_is_zero():
    # Frames shorter than the lookback produce all zeros.
    out = _three([100.0, 101.0, 102.0], [101.0, 102.0, 103.0], [99.0, 100.0, 101.0],
                 [100.5, 101.5, 102.5])
    np.testing.assert_array_equal(out, 0.0)


def test_three_outside_constant_frame_is_zero():
    # A perfectly flat frame (every bar a doji, no engulfing) -> all zeros.
    flat = [100.0] * 20
    out = _three(flat, flat, flat, flat)
    np.testing.assert_array_equal(out, 0.0)


def test_three_outside_output_contract():
    out = INDICATORS.create("three_outside").compute(
        frame(
            [100.0, 99.0, 101.0, 102.0],
            high=[100.0, 100.0, 101.5, 102.5],
            low=[100.0, 98.5, 97.5, 100.5],
            open_=[100.0, 100.0, 98.0, 101.0],
        )
    )
    assert list(out.columns) == ["three_outside"]
    assert set(np.unique(out["three_outside"].to_numpy())) <= {-100.0, 0.0, 100.0}
