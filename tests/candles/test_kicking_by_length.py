"""Kicking-by-length — golden + edge cases (deterministic; no reference library)."""

from __future__ import annotations

import numpy as np

from ohlcv_gen import frame
from pyindicators import INDICATORS
from pyindicators.candles.kicking_by_length import (  # noqa: F401  (import fires @register)
    kicking_by_length,
)

# 11 tiny warm-up bars (small body, small shadows) so BodyLong/ShadowVeryShort averages stay
# small and a genuine marubozu later clears the long-body threshold. TA-Lib lookback = 11.
_WARM = 11
_WO = [100.0] * _WARM
_WC = [100.1] * _WARM
_WH = [100.15] * _WARM
_WL = [99.95] * _WARM


def _kbl(o, h, low, c):
    df = frame(c, high=h, low=low, open_=o)
    return INDICATORS.create("kicking_by_length").compute(df)["kicking_by_length"].to_numpy()


def test_kicking_by_length_bull_current_longer():
    # Black marubozu (120->110, body 10) gaps up to a LONGER white marubozu (130->145, body
    # 15). Sign follows the longer (current, white) candle -> +100 at bar 12.
    o = _WO + [120.0, 130.0]
    c = _WC + [110.0, 145.0]
    h = _WH + [120.0, 145.0]
    low = _WL + [110.0, 130.0]
    assert _kbl(o, h, low, c)[12] == 100.0


def test_kicking_by_length_sign_is_the_longer_marubozu():
    # Same bullish gap-up geometry, but now the PREVIOUS black marubozu (120->105, body 15) is
    # longer than the current white one (130->140, body 10). The longer candle is black, so the
    # signal is -100 -- this is exactly what distinguishes CDLKICKINGBYLENGTH from CDLKICKING.
    o = _WO + [120.0, 130.0]
    c = _WC + [105.0, 140.0]
    h = _WH + [120.0, 140.0]
    low = _WL + [105.0, 130.0]
    assert _kbl(o, h, low, c)[12] == -100.0


def test_kicking_by_length_bear_current_longer():
    # White marubozu (110->120, body 10) gaps down to a LONGER black marubozu (100->80, body
    # 20). Sign follows the longer (current, black) candle -> -100 at bar 12.
    o = _WO + [110.0, 100.0]
    c = _WC + [120.0, 80.0]
    h = _WH + [120.0, 100.0]
    low = _WL + [110.0, 80.0]
    assert _kbl(o, h, low, c)[12] == -100.0


def test_kicking_by_length_no_gap_is_zero():
    # Two opposite marubozu but NO gap (current low 115 <= previous high 120) -> 0.
    o = _WO + [120.0, 115.0]
    c = _WC + [110.0, 130.0]
    h = _WH + [120.0, 130.0]
    low = _WL + [110.0, 115.0]
    assert _kbl(o, h, low, c)[12] == 0.0


def test_kicking_by_length_same_colour_is_zero():
    # Two white candles with a gap up are not opposite colours -> 0.
    o = _WO + [110.0, 130.0]
    c = _WC + [120.0, 145.0]
    h = _WH + [120.0, 145.0]
    low = _WL + [110.0, 130.0]
    assert _kbl(o, h, low, c)[12] == 0.0


def test_kicking_by_length_with_shadows_is_zero():
    # Opposite long bodies with a gap, but the candles have real shadows (not marubozu): the
    # current bar's upper/lower shadows exceed the very-short threshold -> 0.
    o = _WO + [120.0, 130.0]
    c = _WC + [110.0, 145.0]
    h = _WH + [125.0, 150.0]  # large upper shadows
    low = _WL + [105.0, 125.0]  # large lower shadows
    assert _kbl(o, h, low, c)[12] == 0.0


def test_kicking_by_length_constant_frame_is_zero():
    # A flat (open == close, no range) frame has no marubozu and no gaps -> all zeros.
    flat = [100.0] * 30
    out = _kbl(flat, flat, flat, flat)
    np.testing.assert_array_equal(out, 0.0)


def test_kicking_by_length_short_frame_is_zero():
    # Fewer bars than the lookback -> all zeros (no index error).
    o = [100.0, 120.0, 130.0]
    c = [100.1, 110.0, 145.0]
    h = [100.15, 120.0, 145.0]
    low = [99.95, 110.0, 130.0]
    np.testing.assert_array_equal(_kbl(o, h, low, c), 0.0)


def test_kicking_by_length_warmup_is_zero():
    o = _WO + [120.0, 130.0]
    c = _WC + [110.0, 145.0]
    h = _WH + [120.0, 145.0]
    low = _WL + [110.0, 130.0]
    np.testing.assert_array_equal(_kbl(o, h, low, c)[:11], 0.0)  # TA-Lib lookback = 11


def test_kicking_by_length_output_contract():
    o = _WO + [120.0, 130.0]
    c = _WC + [110.0, 145.0]
    h = _WH + [120.0, 145.0]
    low = _WL + [110.0, 130.0]
    out = INDICATORS.create("kicking_by_length").compute(frame(c, high=h, low=low, open_=o))
    assert list(out.columns) == ["kicking_by_length"]
    uniq = set(np.unique(out["kicking_by_length"].to_numpy()))
    assert uniq <= {-100.0, -80.0, 0.0, 80.0, 100.0}
