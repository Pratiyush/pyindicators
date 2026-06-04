"""VPA No Demand "parity" — GOLDEN-ONLY (no reference-library oracle exists).

No charting/TA library in the parity extra (TA-Lib, pandas-ta, finta, ta) implements a
Volume Spread Analysis "No Demand" bar, so there is nothing to compare against. Instead of
a cross-library check, this file pins the indicator to its *closed-form definition*: an
independent, vectorised re-derivation of the rule, asserted bit-for-bit against the
indicator on both synthetic (``deterministic_frame``) and real (``real_frame``) OHLCV.

Rule (spread = high - low): up close AND spread < both prior spreads AND volume < both
prior volumes; the first two bars (no prior pair) are NaN.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, real_frame
from pyindicators import INDICATORS

NAME = "vpa_no_demand"


def _reference(df: pd.DataFrame) -> pd.Series:
    """Independent closed-form re-derivation of the No Demand rule (the oracle)."""
    spread = df["high"] - df["low"]
    vol = df["volume"]
    close = df["close"]
    up_close = close > close.shift(1)
    narrow = (spread < spread.shift(1)) & (spread < spread.shift(2))
    low_vol = (vol < vol.shift(1)) & (vol < vol.shift(2))
    out = pd.Series(np.where(up_close & narrow & low_vol, 1.0, 0.0), index=df.index)
    out.iloc[:2] = np.nan  # two-bar warm-up
    return out


def _assert_matches(df: pd.DataFrame) -> None:
    got = INDICATORS.create(NAME).compute(df)[NAME]
    want = _reference(df)
    # Compare with NaNs aligned (fill to a sentinel the data can never take).
    np.testing.assert_array_equal(got.fillna(-1.0).to_numpy(), want.fillna(-1.0).to_numpy())


def test_closed_form_parity_synthetic():
    _assert_matches(deterministic_frame())


def test_closed_form_parity_real():
    _assert_matches(real_frame())


def test_signal_is_subset_of_up_bars_real():
    # Structural invariant: every No Demand bar is, by construction, an up-close bar.
    df = real_frame()
    out = INDICATORS.create(NAME).compute(df)[NAME]
    fired = out == 1.0
    up = df["close"] > df["close"].shift(1)
    assert fired[fired].index.isin(up[up].index).all()
    assert fired.sum() > 0  # the rule actually triggers on genuine market data
