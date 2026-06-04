# Correctness Audit — base / price_transform / statistics / relative / structure

Independent correctness audit of the 32 in-scope indicators. Each was verified against the
canonical formula and cross-checked against TA-Lib (`talib`), `pandas_ta_classic`, and/or
`finta` on real AAPL daily data (full series + last 150 bars), plus constant / interior-NaN /
2-row edge frames, prefix-vs-full causality, and declared bounds.

**Scope query**

```
uv run python -c "import pyindicators as p; print([(n,p.INDICATORS.get(n).spec.category) \
for n in p.INDICATORS.names() if p.INDICATORS.get(n).spec.category in \
('base','price_transform','statistics','relative','structure')])"
```

**Legend** — Verdict: ✅ verified / ⚠️ concern / ❌ likely bug. Max divergence is `maxabs`
(absolute) on the finite overlap vs the named oracle. The two right-hand columns are the
**per-indicator code review of the implementation source and of its test case**, read
individually.

---

## base

| Indicator | Verdict | Parity (max abs divergence) | Indicator code review (source) | Test-case code review |
|---|---|---|---|---|
| `sma` | ✅ | TA-Lib SMA 1.8e-13; pandas_ta/finta 0.0 | `base/sma.py`: `rolling(length, min_periods=length).mean()`. Correct; `min_periods==length` gives the canonical `length-1` warm-up NaNs. No look-ahead. Clean. | `tests/base/test_sma.py` (4 tests): constant→7.0 + warm-up, linear-ramp closed-form (rtol 1e-12), short-frame all-NaN, function==class. Strong golden coverage. Parity in `test_parity_base.py`. |
| `ema` | ✅ | TA-Lib EMA 5.7e-14 (SMA-seed); `talib_compatible=False`==pandas `ewm(adjust=False)` 0.0 | `base/ema.py`: NumPy loop, `alpha=2/(N+1)`, SMA seed at first valid index, skips a *leading* NaN prefix. Interior NaN poisons forward values — verified identical to TA-Lib. Both seeding modes correct. | `tests/base/test_ema.py` (4 tests): both seed conventions asserted explicitly (SMA-seed value vs pandas first-value), constant, short-frame. Excellent — covers the #1 EMA pitfall. |
| `wma` | ✅ | TA-Lib WMA 3.3e-12; pandas_ta/finta ~4e-14 | `base/wma.py`: weights `arange(1,N+1)` ÷ triangular number, applied via rolling dot. **Weight direction correct** (recent-heavy; ramp→3.667 not reversed 2.333, verified). | `tests/base/test_wma.py` (3 tests): hand-computed WMA(3)=14/6 pins weight direction, constant, short-frame. Good; the known-value test is the key guard. |
| `rma` | ✅ | pandas_ta rma 1.3e-13 | `base/rma.py`: Wilder `alpha=1/N`, SMA seed, leading-NaN skip. Correct recurrence `(prev*(N-1)+x)/N`. | `tests/base/test_rma.py` (3 tests): seed==SMA then one explicit Wilder step asserted, constant, short-frame. Tightly pins the recurrence. |
| `stdev` | ✅ | TA-Lib STDDEV(ddof=0) 1.6e-11; pandas_ta (matched ddof) ~2e-12 | `base/stdev.py`: `rolling.std(ddof=ddof)`, default ddof=0 (population, TA-Lib). Correct. | `tests/base/test_stdev.py` (3 tests): constant→0, population default vs `np.std`, sample `ddof=1` vs `np.std(ddof=1)`. Both ddof branches covered. |
| `variance` | ✅ | TA-Lib VAR(ddof=0) 4.1e-11; pandas_ta (matched ddof) ~6e-12 | `base/variance.py`: `rolling.var(ddof=ddof)`, default 0. Correct, mirrors stdev. | `tests/base/test_variance.py` (3 tests): constant→0, population, sample. Mirrors stdev — complete. |
| `true_range` | ✅ | TA-Lib TRANGE 0.0 (bar 1+); finta TR 0.0 (incl. bar 0) | `base/true_range.py`: `max(H-L, |H-prevC|, |L-prevC|)`; bar 0 → H-L (documented TA-Lib divergence). Correct. | `tests/base/test_true_range.py` (3 tests): bar-0 fallback, gap-uses-prev-close hand value (2.0), flat→0. Parity test documents the bar-0 mask. Excellent. |

## price_transform

| Indicator | Verdict | Parity (max abs divergence) | Indicator code review (source) | Test-case code review |
|---|---|---|---|---|
| `hl2` | ✅ | TA-Lib MEDPRICE 0.0 | `price_transform/hl2.py`: `(H+L)/2`. Exact, no warm-up. | `tests/price_transform/test_transforms.py::test_hl2`: 2-bar hand value. Parity vs MEDPRICE. Adequate (trivial transform). |
| `hlc3` | ✅ | TA-Lib TYPPRICE 0.0 | `hlc3.py`: `(H+L+C)/3`. Exact. | `::test_hlc3`: hand value (12+6+9)/3. Parity vs TYPPRICE. Adequate. |
| `ohlc4` | ✅ | TA-Lib AVGPRICE 2.8e-14 | `ohlc4.py`: `(O+H+L+C)/4`. Exact. | `::test_ohlc4`: hand value. Parity vs AVGPRICE. Adequate. |
| `wcp` | ✅ | TA-Lib WCLPRICE 0.0 | `wcp.py`: `(H+L+2C)/4`. Correct double-weight on close. | `::test_wcp`: hand value pins the 2× close weight. Parity vs WCLPRICE. Adequate. |
| `midpoint` | ✅ | TA-Lib MIDPOINT 0.0 | `midpoint.py`: `(maxC+minC)/2` over N. Correct. | `::test_midpoint`: two hand values on a 5-bar series. Parity vs MIDPOINT. Good. |
| `midprice` | ✅ | TA-Lib MIDPRICE 0.0 | `midprice.py`: `(maxH+minL)/2` over N. Correct (uses H/L, not close). | `::test_midprice`: hand value with distinct H/L. Parity vs MIDPRICE. Good. |
| `heikin_ashi` | ✅ | pandas_ta `ha` 0.0 across all 506 bars | `heikin_ashi.py`: HA_Close=ohlc4; HA_Open recursive, seed `(O₀+C₀)/2`; HA_High/Low via max/min. Recursion + seed verified exact vs pandas_ta. | `::test_heikin_ashi`: asserts HA_Close vector, seed at bar 0, one recursive HA_Open step, and HA_High max. Parity asserts all 4 outputs vs pandas_ta. Strong — covers the recursive pitfall. |

## statistics

| Indicator | Verdict | Parity (max abs divergence) | Indicator code review (source) | Test-case code review |
|---|---|---|---|---|
| `linreg` | ✅ | TA-Lib LINEARREG 2.4e-13; pandas_ta 1.7e-13 | `statistics/linreg.py` + `_ols.py`: OLS via normal equations, endpoint `intercept+slope*(N-1)`. Convention confirmed against TA-Lib. | `tests/statistics/test_linreg.py::test_linreg_on_perfect_line`: y=2x+10 recovered exactly; also `test_flat_series_slope_zero`. Parity in `test_parity_linreg.py`. Strong. |
| `linreg_slope` | ✅ | TA-Lib LINEARREG_SLOPE 3.7e-14 | `linreg_slope.py`: `rolling_ols(...)[0]`. OLS slope (NOT the secant `diff/n` that `pandas_ta.slope` uses — that mismatch is expected, ours matches TA-Lib). | Covered by `test_linreg_on_perfect_line` (slope==2) + `test_flat_series_slope_zero` + parity vs LINEARREG_SLOPE. Solid. |
| `linreg_intercept` | ✅ | TA-Lib LINEARREG_INTERCEPT 2.3e-13 | `linreg_intercept.py`: `rolling_ols(...)[1]` = value at x=0 (window start). Convention confirmed vs TA-Lib. | Asserted in `test_linreg_on_perfect_line` (intercept==y[t-4]) + parity vs LINEARREG_INTERCEPT. Adequate; no standalone unit test but the perfect-line + parity pin it. |
| `linreg_angle` | ✅ | TA-Lib LINEARREG_ANGLE 1.5e-12; bound [-90,90] held (obs [-55.5,47.8]) | `linreg_angle.py`: `degrees(arctan(slope))`. Correct; bound declared and respected. | `test_linreg_angle_of_known_slope`: slope 1 → 45°. Parity vs LINEARREG_ANGLE. Good. |
| `tsf` | ✅ | TA-Lib TSF 2.8e-13; pandas_ta 2.0e-13 | `tsf.py`: `intercept+slope*N` = 1-bar forecast (vs linreg's `N-1`). Off-by-one convention confirmed vs TA-Lib. | Asserted in `test_linreg_on_perfect_line` (tsf==y[t]+2) + parity vs TSF. Adequate (no standalone unit test, but forecast offset is pinned). |
| `zscore` | ✅ | pandas_ta zscore 2.2e-12 | `zscore.py`: `(c-SMA)/stdev`, default ddof=1 (sample, matches pandas_ta default); `safe_divide` guards flat windows. Correct. | `tests/statistics/test_statistics.py`: constant→NaN (guard) + finite-on-trend. Parity vs pandas_ta. Good — exercises the /0 guard. |
| `mad` | ✅ | pandas_ta mad 0.0 | `mad.py`: rolling `mean(|w-mean(w)|)`. Correct mean-absolute-deviation. | `test_mad_constant_is_zero`. Parity vs pandas_ta. Thin (only constant), but parity over 400 bars carries it. |
| `median` | ✅ | pandas_ta median 0.0 | `median.py`: `rolling.median()`. Correct. | `test_median_known`: two hand medians on odd windows. Parity vs pandas_ta. Good. |
| `quantile` | ✅ | pandas_ta quantile 0.0 | `quantile.py`: `rolling.quantile(q)`, q∈[0,1] validated. Correct. | `test_quantile_extremes`: q=0→min, q=1→max. No parity test in `test_parity_statistics.py`, but q=0/1 endpoints + pandas passthrough are sound. Adequate. |
| `skew` | ✅ | pandas_ta skew 4.9e-11 | `skew.py`: `rolling.skew()` (Fisher-Pearson adjusted, matches pandas_ta). Correct; needs ≥3 pts (`ge=3`). | `test_skew_kurtosis_finite` (finite on 100-bar walk). Parity vs pandas_ta (the real guard). No golden value — relies on parity. Acceptable. |
| `kurtosis` | ✅ | pandas_ta kurtosis 9.4e-10 | `kurtosis.py`: `rolling.kurt()` (excess kurtosis, matches pandas_ta). Correct; needs ≥4 pts (`ge=4`). | Shares `test_skew_kurtosis_finite`. Parity vs pandas_ta. Same note as skew — parity-carried. |
| `entropy` | ✅ | pandas_ta entropy 1.3e-15 | `entropy.py`: per-window `p=w/sum(w)`, `Σ(-p·ln p)/ln(base)`. Proper per-window Shannon; constant→log_base(N). Correct (relies on prices>0). | `test_entropy_constant_is_log_n`: constant→log2(8) exactly. Parity vs pandas_ta. Strong — the constant identity is the right invariant. |
| `hurst_exponent` | ✅ | structural (no oracle): random-walk→~0.5 | `hurst_exponent.py`: R/S of log returns, `H=log(R/S)/log(n)`; flat window→NaN. 5000-bar walk → mean 0.528 (correct, with known small-sample R/S upward bias). | `tests/statistics/test_hurst.py` (2 tests): random-walk in sane band (0.2–0.9), flat→NaN. Reasonable for a no-oracle estimator; band is wide but appropriate given R/S variance. |

## relative

| Indicator | Verdict | Parity (max abs divergence) | Indicator code review (source) | Test-case code review |
|---|---|---|---|---|
| `rs_rating` | ✅ | matches manual weighted-ratio 0.0; flat→1.0 | `relative/rs_rating.py`: `Σ wᵢ·(c/c.shift(lbᵢ)) / Σwᵢ`. Correct weighted multi-period momentum; flat series → exactly 1.0; weights (2,1,1,1)/5. Per-symbol score (cross-sectional ranking intentionally left to the screener). | `tests/relative/test_rs_rating.py` (3 tests): constant→1.0, uptrend>1, default finite on 300 bars. Pins the flat-identity and direction. Good for a bespoke (non-oracle) score. |

## structure

| Indicator | Verdict | Parity (max abs divergence) | Indicator code review (source) | Test-case code review |
|---|---|---|---|---|
| `rolling_high` | ✅ | trailing-max (no oracle); causal | `structure/rolling_high.py`: `H.rolling(N).max()`. Correct; window includes current bar (no look-ahead). | `tests/structure/test_structure.py::test_rolling_high_low_on_ramp`: rising series → max==current bar. Short-frame all-NaN. Good. |
| `rolling_low` | ✅ | trailing-min (no oracle); causal | `rolling_low.py`: `L.rolling(N).min()`. Correct. | Shares `test_rolling_high_low_on_ramp`: min==2 bars back on a ramp. Good. |
| `pct_from_high` | ✅ | real-data range [-32.06, -0.023] (always ≤0) | `pct_from_high.py`: `100·(c-HH)/HH`, HH includes today's high so result ≤0; `safe_divide` guards. Correct. | `test_pct_from_high_at_new_high_is_zero`: at-high→0. Good; the sign/zero identity is the key invariant. |
| `pct_from_low` | ✅ | real-data range [0.72, 51.46] (always ≥0) | `pct_from_low.py`: `100·(c-LL)/LL`, ≥0 since c≥LL; guarded. Correct. | `test_pct_from_low_is_positive_above_low`: strictly >0 above low. Good. |

---

## Cross-cutting checks

- **Causality (no look-ahead):** prefix-vs-full outputs identical on overlap for all 32.
- **Edge frames:** no crashes, no infinities, no spurious bound breaks. All-NaN cases
  (constant + `zscore`/`hurst_exponent`; 2-row warm-up; interior-NaN `ema`/`rma`) are all
  by-design and TA-Lib-consistent.
- **Bounds:** `linreg_angle` declared `[-90, 90]`, observed `[-55.5, 47.8]`.
- **Suite:** all in-scope unit + parity tests pass under `uv run --extra parity python -m pytest`.

## Test-coverage observations (no correctness impact)

- `linreg_intercept` and `tsf` have **no standalone unit test** — both are asserted inside
  `test_linreg_on_perfect_line` and covered by `test_parity_linreg.py`, which is sufficient,
  but a dedicated golden value would make each self-documenting.
- `quantile` has **no entry** in `test_parity_statistics.py` (unit test covers q=0/1 only).
- `skew` / `kurtosis` have **no golden value** — correctness rests on the pandas_ta parity
  test plus a finiteness check; fine given they are thin wrappers over pandas moments.
- `mad` unit coverage is only the constant→0 case; parity over 400 bars carries it.

## Counts

- ✅ Verified: **32**
- ⚠️ Concerns: **0**
- ❌ Likely bugs: **0**
