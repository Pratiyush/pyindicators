"""Tasuki Gap — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.tasuki_gap import tasuki_gap  # noqa: F401  (import fires @register)

# 7 warm-up bars so the Near average (HighLow/5/0.2) is defined by bar 7; the pattern then forms
# across candles 7 (pre-gap), 8 (gapping), 9 (continuation) and is reported at bar 9.
_WARM = 7
_WO = [50.0] * _WARM
_WC = [50.2] * _WARM
_WH = [50.4] * _WARM
_WL = [49.6] * _WARM


def _tg(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("tasuki_gap").compute(df)["tasuki_gap"].to_numpy()


def test_tasuki_gap_upside_is_100():
    # 7: pre-gap (body_hi 50.3); 8: white gaps up (body_lo 51.0); 9: black opens within the
    # white body and closes back into the gap (above 50.3) -> +100 (gapping candle is white).
    o = _WO + [50.0, 51.0, 51.5]
    c = _WC + [50.3, 52.0, 50.6]
    h = _WH + [50.5, 52.2, 51.7]
    low = _WL + [49.9, 50.9, 50.4]
    assert _tg(o, h, low, c)[9] == 100.0


def test_tasuki_gap_downside_is_minus_100():
    # 7: pre-gap (body_lo 52.0); 8: black gaps down (body_hi 51.0); 9: white opens within the
    # black body and closes back into the gap (below 52.0) -> -100 (gapping candle is black).
    o = _WO + [52.0, 51.0, 50.5]
    c = _WC + [52.3, 50.0, 51.5]
    h = _WH + [52.5, 51.2, 51.7]
    low = _WL + [51.9, 49.8, 50.3]
    assert _tg(o, h, low, c)[9] == -100.0


def test_tasuki_gap_no_gap_is_zero():
    # The gapping candle does not gap over the pre-gap body -> not a tasuki gap -> 0.
    o = _WO + [50.0, 50.1, 50.6]
    c = _WC + [50.3, 51.0, 50.2]
    h = _WH + [50.5, 51.2, 50.7]
    low = _WL + [49.9, 50.0, 50.0]
    assert _tg(o, h, low, c)[9] == 0.0


def test_tasuki_gap_warmup_is_zero():
    o = _WO + [50.0, 51.0, 51.5]
    c = _WC + [50.3, 52.0, 50.6]
    h = _WH + [50.5, 52.2, 51.7]
    low = _WL + [49.9, 50.9, 50.4]
    np.testing.assert_array_equal(_tg(o, h, low, c)[:7], 0.0)  # TA-Lib lookback = 7


def test_tasuki_gap_constant_frame_is_zero():
    # A flat (doji) series can never gap -> all zeros, never NaN.
    flat = [100.0] * 40
    out = _tg(flat, flat, flat, flat)
    np.testing.assert_array_equal(out, 0.0)


def test_tasuki_gap_short_frame_is_zero():
    # Frames shorter than the lookback produce all zeros (no NaN, no out-of-range index).
    for length in range(1, 8):
        seq = [100.0 + i for i in range(length)]
        out = _tg(seq, [v + 0.5 for v in seq], [v - 0.5 for v in seq], [v + 0.2 for v in seq])
        assert out.shape == (length,)
        np.testing.assert_array_equal(out, 0.0)


def test_tasuki_gap_output_contract():
    o = _WO + [50.0, 51.0, 51.5]
    c = _WC + [50.3, 52.0, 50.6]
    h = _WH + [50.5, 52.2, 51.7]
    low = _WL + [49.9, 50.9, 50.4]
    out = INDICATORS.create("tasuki_gap").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["tasuki_gap"]
    assert set(np.unique(out["tasuki_gap"].to_numpy())) <= {-100.0, -80.0, 0.0, 80.0, 100.0}
