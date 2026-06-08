"""Real-data invariants for every registered indicator (genuine AAPL daily bars).

This is the pytest counterpart of ``scripts/audit_indicators.py`` stages 1-2, pinned on real
market data so the whole registry carries real-data regression coverage (not only the synthetic
walk): for each indicator on ``real_frame()`` we assert length preservation, no infinities, at
least one finite value, declared bounds, determinism, and — for causal indicators — no
look-ahead (a truncated compute equals the prefix of the full compute).

The indicator list is spelled out literally (not derived from the registry at runtime) so the
build-tracking / audit "real-data coverage" detectors, which scan for quoted names, see every
one. ``tests/meta`` guards that this list stays in sync with the registry.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from ohlcv_gen import real_frame
from pyindicators import INDICATORS

REAL = real_frame()

ALL_INDICATORS = [
    'abandoned_baby', 'aberration', 'accbands', 'acos', 'ad', 'add', 'adosc', 'advance_block',
    'adx', 'adxr', 'alligator', 'alma', 'amat', 'ao', 'aobv', 'apo', 'apz', 'aroon', 'aroon_osc',
    'asin', 'atan', 'atr', 'bbands', 'belt_hold', 'beta', 'bias', 'big_shadow', 'bop', 'brar',
    'breakaway', 'cci', 'ceil', 'cfo', 'cg', 'chandelier', 'chop', 'cksp', 'closing_marubozu',
    'cmb_composite_index', 'cmf', 'cmo', 'conceal_baby_swallow', 'coppock', 'correl', 'cos', 'cosh',
    'counterattack', 'covariance', 'crsi', 'cti', 'cvi', 'dark_cloud_cover', 'decay', 'decreasing',
    'dema', 'demarker', 'derivative_osc', 'disparity_index', 'div', 'doji', 'doji_star', 'donchian',
    'dpo', 'dragonfly_doji', 'dsp', 'dx', 'ebsw', 'edecay', 'efi', 'ema', 'engulfing', 'entropy',
    'eom', 'er', 'eri', 'evening_doji_star', 'evening_star', 'evwma', 'exp', 'fama', 'fisher',
    'floor', 'fosc', 'frama', 'fve', 'fwma', 'gap_side_side_white', 'gator', 'gravestone_doji',
    'hammer', 'hanging_man', 'harami', 'harami_cross', 'heikin_ashi', 'high_wave', 'hikkake',
    'hikkake_mod', 'hilo', 'hl2', 'hlc3', 'hma', 'homing_pigeon', 'ht_dcperiod', 'ht_dcphase',
    'ht_phasor', 'ht_sine', 'ht_trendline', 'ht_trendmode', 'hurst_exponent', 'hv', 'hwc', 'hwma',
    'ichimoku', 'identical_three_crows', 'in_neck', 'increasing', 'inertia', 'inverted_hammer',
    'jma', 'kama', 'kangaroo_tail', 'kdj', 'keltner', 'kicking', 'kicking_by_length', 'kst',
    'kurtosis', 'kvo', 'ladder_bottom', 'lag', 'laguerre_rsi', 'linreg', 'linreg_angle',
    'linreg_intercept', 'linreg_slope', 'ln', 'log10', 'long_legged_doji', 'long_line', 'long_run',
    'lsma', 'ma_spread', 'macd', 'macdext', 'macdfix', 'mad', 'mama', 'marketfi', 'marubozu',
    'massi', 'mat_hold', 'matching_low', 'max', 'maxindex', 'mcgd', 'median', 'mfi', 'midpoint',
    'midprice', 'min', 'minindex', 'minmax', 'minmaxindex', 'minus_di', 'minus_dm', 'mom',
    'morning_doji_star', 'morning_star', 'msw', 'mult', 'natr', 'nvi', 'obv', 'ohlc4', 'on_neck',
    'pct_from_high', 'pct_from_low', 'pdist', 'percent_rank', 'pgo', 'piercing', 'pivots',
    'plus_di', 'plus_dm', 'pmax', 'ppo', 'psar', 'psl', 'pvi', 'pvo', 'pvol', 'pvr', 'pvt', 'pwma',
    'qqe', 'qstick', 'quantile', 'r_squared', 'rainbow', 'rickshaw_man', 'rise_fall_three_methods',
    'rma', 'roc', 'roc1', 'rocp', 'rocr', 'rocr100', 'rolling_high', 'rolling_low', 'rs_rating',
    'rsi', 'rsi_negative_reversal', 'rsi_positive_reversal', 'rsl', 'rsx', 'rvgi', 'rvi', 'rvol',
    'sarext', 'separating_lines', 'shooting_star', 'short_line', 'short_run', 'sin', 'sinh',
    'sinwma', 'skew', 'slope', 'sma', 'sma_slope', 'smi', 'spinning_top', 'spring', 'sqrt',
    'squeeze', 'squeeze_pro', 'ssf', 'stalled_pattern', 'starc', 'stc', 'stderr', 'stdev',
    'stick_sandwich', 'stoch', 'stochf', 'stochrsi', 'sub', 'sum', 'supertrend', 'swma', 't3',
    'takuri', 'tan', 'tanh', 'tasuki_gap', 'td_seq', 'tema', 'thermo', 'three_black_crows',
    'three_inside', 'three_line_strike', 'three_outside', 'three_stars_in_south',
    'three_white_soldiers', 'thrusting', 'tos_stdevall', 'trima', 'tristar', 'trix', 'true_range',
    'tsf', 'tsi', 'ttm_momentum', 'ttm_trend', 'two_crows', 'ulcer', 'unique_three_river', 'uo',
    'upside_gap_two_crows', 'upthrust', 'vama', 'variance', 'vfi', 'vhf', 'vidya', 'vol_sma',
    'vortex', 'vpa_climactic_bars', 'vpa_effort_vs_result', 'vpa_no_demand', 'vpa_no_supply',
    'vpa_stopping_volume', 'vwap', 'vwma', 'vwmacd', 'wad', 'wcp', 'willr', 'wma',
    'xside_gap_three_methods', 'zlma', 'zscore',
]


# arccos/arcsin are undefined for |x| > 1, so on genuine price inputs they are *correctly*
# all-NaN — the one case where "at least one finite value" must not be required.
_DOMAIN_LIMITED = {"acos", "asin"}


def test_indicator_list_matches_registry():
    """The literal list above must equal the live registry (so coverage can't silently drift)."""
    assert sorted(ALL_INDICATORS) == sorted(INDICATORS.names())


@pytest.mark.parametrize("name", ALL_INDICATORS)
def test_real_data_invariants(name):
    ind = INDICATORS.create(name)
    out = pd.DataFrame(ind.compute(REAL))

    # Stage 1 — robustness: length preserved, finite values exist, no infinities, bounds hold.
    assert len(out) == len(REAL)
    arr = out.to_numpy(dtype="float64")
    if name in _DOMAIN_LIMITED:
        assert np.isnan(arr).all()  # price inputs are out of arccos/arcsin domain
    else:
        assert np.isfinite(arr).any()
    assert not np.isinf(arr).any()
    for col, (lo, hi) in (ind.spec.bounds or {}).items():
        v = out[col].to_numpy(dtype="float64")
        v = v[np.isfinite(v)]
        if v.size:
            assert v.min() >= lo - 1e-9 and v.max() <= hi + 1e-9

    # Stage 2 — determinism + no look-ahead (causal indicators only).
    again = pd.DataFrame(INDICATORS.create(name).compute(REAL))
    assert out.equals(again)
    if ind.spec.causal:
        k = len(REAL) // 2
        trunc = pd.DataFrame(INDICATORS.create(name).compute(REAL.iloc[:k].copy()))
        a = out.to_numpy(dtype="float64")[:k]
        b = trunc.to_numpy(dtype="float64")
        mask = np.isfinite(a) & np.isfinite(b)
        np.testing.assert_allclose(a[mask], b[mask], rtol=1e-9, atol=1e-9)
