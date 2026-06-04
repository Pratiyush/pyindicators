"""Gann HiLo Activator — golden / closed-form + edge cases."""

from __future__ import annotations

import numpy as np
import pandas as pd

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.base import sma
from pyindicators.trend.hilo import hilo  # noqa: F401  (import fires @register for create())


def _create(**kw):
    return INDICATORS.create("hilo", **kw)


def test_steady_uptrend_tracks_low_band_in_long_leg():
    # In an unbroken uptrend every bar crosses above the prior high-band, so the line pins to
    # the low-band SMA and lives entirely in the long leg; the short leg never fires.
    close = np.arange(10.0, 30.0)
    df = frame(close, high=close + 0.5, low=close - 0.5)
    out = _create(high_length=2, low_length=3).compute(df)
    expected = sma(df["low"], 3)
    np.testing.assert_allclose(out["hilo"].to_numpy(), expected.to_numpy(), equal_nan=True)
    np.testing.assert_allclose(out["hilo_long"].to_numpy(), expected.to_numpy(), equal_nan=True)
    assert out["hilo_short"].isna().all()


def test_steady_downtrend_tracks_high_band_in_short_leg():
    # Mirror image: a monotonic decline keeps the line on the high-band SMA in the short leg.
    close = np.arange(30.0, 10.0, -1.0)
    df = frame(close, high=close + 0.5, low=close - 0.5)
    out = _create(high_length=2, low_length=3).compute(df)
    high_sma = sma(df["high"], 2).to_numpy()
    line = out["hilo"].to_numpy()
    mask = np.isfinite(line)
    np.testing.assert_allclose(line[mask], high_sma[mask])
    # Everything defined is short-leg; long leg stays empty in a pure downtrend.
    np.testing.assert_allclose(out["hilo_short"].to_numpy(), line, equal_nan=True)
    assert out["hilo_long"].isna().all()


def test_legs_reconstruct_line_and_carry_bars_set_both():
    # long.fillna(short) must rebuild hilo wherever defined; and at least one carry-forward
    # bar sets BOTH legs (the documented non-exclusive carry behaviour).
    df = deterministic_frame(150)
    out = _create(high_length=13, low_length=21).compute(df)
    line, long_leg, short_leg = out["hilo"], out["hilo_long"], out["hilo_short"]
    recon = long_leg.fillna(short_leg).dropna()
    np.testing.assert_allclose(recon.to_numpy(), line.loc[recon.index].to_numpy())
    both_set = (~long_leg.isna()) & (~short_leg.isna())
    assert both_set.sum() > 0


def test_warmup_is_max_of_lengths():
    # Nothing can flip until the *longer* SMA exists, so the first finite bar is no earlier
    # than index low_length-1 here (low_length is the larger window).
    df = deterministic_frame(120)
    out = _create(high_length=13, low_length=21).compute(df)
    first = out["hilo"].first_valid_index()
    assert first is not None and first >= 20


def test_flat_series_never_crosses_all_nan():
    # Strict comparisons (`<` / `>`) mean a constant series never crosses a band -> all NaN.
    df = frame(np.full(40, 50.0))
    out = _create(high_length=13, low_length=21).compute(df)
    assert out["hilo"].isna().all()
    assert out["hilo_long"].isna().all()
    assert out["hilo_short"].isna().all()


def test_short_frame_all_nan():
    df = frame([1.0, 2.0, 3.0])
    out = _create(high_length=13, low_length=21).compute(df)
    assert out.isna().all().all()


def test_causal_no_lookahead():
    # Appending future bars must not change already-computed values (path-dependent but causal).
    df = deterministic_frame(200)
    full = _create().compute(df)
    head = _create().compute(df.iloc[:120].copy())
    common = full.iloc[:120]
    for col in ("hilo", "hilo_long", "hilo_short"):
        a, b = head[col].to_numpy(), common[col].to_numpy()
        mask = np.isfinite(a) & np.isfinite(b)
        np.testing.assert_allclose(a[mask], b[mask])


def test_output_contract():
    df = deterministic_frame(80)
    out = _create().compute(df)
    assert list(out.columns) == ["hilo", "hilo_long", "hilo_short"]
    assert (out.dtypes == np.float64).all()
    assert len(out) == len(df)
    assert isinstance(out, pd.DataFrame)
