"""RSI Positive Reversal (Cardwell) — golden, causal, and edge-case tests.

There is no reference-library oracle for Cardwell reversals, so the explicit 3-bar-trough
rule is pinned on hand-built sequences (RSI ``length=3`` for a short warm-up) with the exact
0/1 array hard-coded, plus a direct truncation-invariance check of causality.
"""

from __future__ import annotations

import numpy as np
import pytest
from pydantic import ValidationError

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS

# Importing the module registers the indicator so INDICATORS.create can find it.
from pyindicators.momentum.rsi_positive_reversal import rsi_positive_reversal  # noqa: F401

# Hand-built scenario: two strict 3-bar RSI troughs at t=5 and t=9.
#   trough@5: RSI 33.333, low 8.0   |   trough@9: RSI 60.099 (HIGHER), low 7.0 (LOWER)
# -> positive reversal; the flag fires at the CONFIRMATION bar t+1 = 10.
_POS_CLOSE = [10, 11, 12, 13, 14, 10, 13, 14, 15, 14.2, 16, 17, 18]
_POS_LOW = [10, 11, 12, 13, 14, 8.0, 13, 14, 15, 7.0, 16, 17, 18]
_POS_EXPECT = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0], dtype="float64")


def _run(close, low, length=3):
    df = frame(close, low=low)
    return INDICATORS.create("rsi_positive_reversal", length=length).compute(df)


def test_golden_positive_reversal_fires_at_confirmation_bar():
    out = _run(_POS_CLOSE, _POS_LOW)["rsi_positive_reversal"].to_numpy()
    np.testing.assert_array_equal(out, _POS_EXPECT)
    # The single signal sits on the bar AFTER the second trough (t=9), never on the trough.
    assert np.flatnonzero(out).tolist() == [10]


def test_no_signal_when_rsi_makes_lower_low():
    # Same swings but the second close dip is DEEPER, so RSI prints a LOWER low (33->... lower):
    # the bullish divergence is absent -> no positive reversal anywhere.
    close = [10, 11, 12, 13, 14, 12, 14, 15, 16, 13.5, 16, 17, 18]
    low = [10, 11, 12, 13, 14, 9.0, 14, 15, 16, 8.0, 16, 17, 18]
    out = _run(close, low)["rsi_positive_reversal"].to_numpy()
    assert out.sum() == 0.0


def test_no_signal_when_price_low_not_lower():
    # RSI makes a higher low (shallow second close dip) BUT the price low is also HIGHER,
    # so the price-vs-oscillator disagreement that defines the signal is missing.
    close = [10, 11, 12, 13, 14, 10, 13, 14, 15, 14.2, 16, 17, 18]
    low = [10, 11, 12, 13, 14, 8.0, 13, 14, 15, 9.0, 16, 17, 18]  # 9.0 > 8.0
    out = _run(close, low)["rsi_positive_reversal"].to_numpy()
    assert out.sum() == 0.0


def test_first_trough_alone_never_signals():
    # Only one detectable RSI trough exists -> nothing to compare against -> all zeros.
    close = [10, 11, 12, 13, 14, 10, 13, 14, 15, 16, 17]
    low = [10, 11, 12, 13, 14, 8.0, 13, 14, 15, 16, 17]
    out = _run(close, low)["rsi_positive_reversal"].to_numpy()
    assert out.sum() == 0.0


def test_output_is_strictly_binary_and_contract():
    out = INDICATORS.create("rsi_positive_reversal", length=14).compute(deterministic_frame(300))
    assert tuple(out.columns) == ("rsi_positive_reversal",)
    vals = out["rsi_positive_reversal"].to_numpy()
    assert str(out["rsi_positive_reversal"].dtype) == "float64"
    assert np.isin(vals, (0.0, 1.0)).all()  # never NaN, never anything but 0/1
    assert np.isfinite(vals).all()


def test_causal_truncation_invariance_on_golden():
    # The flag at the confirmation bar must be reproducible from a frame truncated there, and
    # must NOT appear from a frame that ends on the trough bar itself (no look-ahead).
    df = frame(_POS_CLOSE, low=_POS_LOW)
    ind = INDICATORS.create("rsi_positive_reversal", length=3)
    full = ind.compute(df)["rsi_positive_reversal"].to_numpy()
    for k in (9, 10, 11, len(_POS_CLOSE)):
        trunc = ind.compute(df.iloc[:k].copy())["rsi_positive_reversal"].to_numpy()
        np.testing.assert_array_equal(trunc, full[:k])
    # ending ON the trough (k=10 -> last index 9) cannot yet know the signal:
    end_on_trough = ind.compute(df.iloc[:10].copy())["rsi_positive_reversal"].to_numpy()
    assert end_on_trough.sum() == 0.0


def test_short_frame_all_zero():
    out = _run([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])["rsi_positive_reversal"].to_numpy()
    assert out.sum() == 0.0
    assert len(out) == 3


def test_length_param_is_validated():
    # extra='forbid' + ge=1 on Params: bad inputs are rejected at construction.
    with pytest.raises(ValidationError):
        INDICATORS.create("rsi_positive_reversal", bogus=1)
    with pytest.raises(ValidationError):
        INDICATORS.create("rsi_positive_reversal", length=0)
