"""TOS StDevAll — golden formula (OLS line + k-stdev bands) and edge cases.

Imported directly so ``@INDICATORS.register`` fires, then driven via ``INDICATORS.create``.
"""

from __future__ import annotations

import numpy as np

from ohlcv_gen import deterministic_frame, frame
from pyindicators import INDICATORS
from pyindicators.statistics.tos_stdevall import tos_stdevall  # noqa: F401  (registers indicator)

_COLS = (
    "tos_stdevall_lr",
    "tos_stdevall_l_1",
    "tos_stdevall_u_1",
    "tos_stdevall_l_2",
    "tos_stdevall_u_2",
    "tos_stdevall_l_3",
    "tos_stdevall_u_3",
)


def test_columns_and_full_length_no_warmup():
    df = deterministic_frame(120)
    out = INDICATORS.create("tos_stdevall").compute(df)
    assert list(out.columns) == list(_COLS)
    assert len(out) == len(df)
    # Non-causal full-window fit -> no warm-up NaNs anywhere.
    assert not out.isna().to_numpy().any()


def test_golden_on_perfect_line():
    # On an exact line y = 5 + 2x the OLS fit is the line itself, so LR == y everywhere and the
    # bands are LR +/- k*sample_stdev(y). Golden-checks the OLS recovery and the band offsets.
    y = 5.0 + 2.0 * np.arange(40.0)
    out = INDICATORS.create("tos_stdevall", ddof=1).compute(frame(y))
    lr = out["tos_stdevall_lr"].to_numpy()
    np.testing.assert_allclose(lr, y, atol=1e-9)
    sd = float(np.std(y, ddof=1))
    for k in (1, 2, 3):
        np.testing.assert_allclose(out[f"tos_stdevall_l_{k}"].to_numpy(), y - k * sd, atol=1e-9)
        np.testing.assert_allclose(out[f"tos_stdevall_u_{k}"].to_numpy(), y + k * sd, atol=1e-9)


def test_bands_symmetric_and_ordered():
    out = INDICATORS.create("tos_stdevall").compute(deterministic_frame(80))
    lr = out["tos_stdevall_lr"].to_numpy()
    # Symmetric about LR and strictly widening with k (positive stdev on a real walk).
    for k in (1, 2, 3):
        lo = out[f"tos_stdevall_l_{k}"].to_numpy()
        up = out[f"tos_stdevall_u_{k}"].to_numpy()
        np.testing.assert_allclose(lr - lo, up - lr, atol=1e-9)
        assert np.all(up > lr) and np.all(lo < lr)
    assert np.all(out["tos_stdevall_u_3"].to_numpy() > out["tos_stdevall_u_1"].to_numpy())
    assert np.all(out["tos_stdevall_l_3"].to_numpy() < out["tos_stdevall_l_1"].to_numpy())


def test_flat_series_collapses_bands_to_line():
    # stdev == 0 on a constant series -> bands collapse onto the (horizontal) LR line, no NaN.
    out = INDICATORS.create("tos_stdevall").compute(frame([42.0] * 30))
    np.testing.assert_allclose(out["tos_stdevall_lr"].to_numpy(), 42.0, atol=1e-9)
    for k in (1, 2, 3):
        np.testing.assert_allclose(out[f"tos_stdevall_l_{k}"].to_numpy(), 42.0, atol=1e-9)
        np.testing.assert_allclose(out[f"tos_stdevall_u_{k}"].to_numpy(), 42.0, atol=1e-9)


def test_single_bar_is_horizontal_at_value():
    # n == 1: polyfit -> slope 0, line at the lone value; stdev undefined -> bands collapse.
    out = INDICATORS.create("tos_stdevall").compute(frame([7.0]))
    assert len(out) == 1
    for col in _COLS:
        np.testing.assert_allclose(out[col].to_numpy(), 7.0, atol=1e-9)


def test_empty_frame_returns_empty():
    out = INDICATORS.create("tos_stdevall").compute(frame([]))
    assert list(out.columns) == list(_COLS)
    assert len(out) == 0
