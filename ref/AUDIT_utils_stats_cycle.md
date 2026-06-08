# Correctness Review — utils (9) + statistics extras (6) + cycle (9)

Line-by-line review of three small families. Each indicator was read against its canonical
definition and confirmed causal; every one has a parity test under `tests/parity/`.

**Legend** — Verdict: ✅ verified.

## utils (9)

| Indicator | Verdict | Source review | Test review |
|---|---|---|---|
| `crossover` | ✅ | `(a > b) & (a.shift(1) < b.shift(1))` — strict edge: a was below, now above. Causal. | golden (hand values) + parity vs `pandas_ta.cross(above=True)` on the post-warmup region. |
| `crossunder` | ✅ | `(a < b) & (a.shift(1) > b.shift(1))` — strict down-edge. | golden + parity vs `pandas_ta.cross(above=False)`. |
| `crossany` | ✅ | logical OR of crossover/crossunder. | golden + parity. |
| `cross_value` | ✅ | crossover/crossunder of a series vs a constant level. | golden + parity vs `pandas_ta.cross_value`. |
| `lag` | ✅ | `close.shift(length)` — definition *is* `Series.shift`. | golden vs shift; parity. |
| `decay` | ✅ | linear decay of the *previous close* (`max(close, prev-1/length)`), matching pandas-ta. | parity vs `pandas_ta.decay`. |
| `edecay` | ✅ | exponential decay `prev * exp(-1/length)` — documented as distinct from `decay`. | parity vs `pandas_ta` exp-decay. |
| `percent_rank` | ✅ | rolling percentile rank over the `length` bars *before* the current bar (`shift(1)` window). Causal. | parity. |
| `roc1` | ✅ | one-bar rate of change (zero-param building block). | parity vs 1-period ROC. |

## statistics extras (6) — completing the statistics family (the other 13 are in `AUDIT_base_pricetransform_stats_relative_structure.md`)

| Indicator | Verdict | Source review | Test review |
|---|---|---|---|
| `correl` | ✅ | rolling Pearson correlation (pandas `rolling.corr`), clamped against ~1e-15 overshoot. | parity vs `talib.CORREL`. |
| `beta` | ✅ | rolling OLS slope of high vs low (market beta) via rolling sums. | parity vs `talib.BETA`. |
| `covariance` | ✅ | sample covariance (`ddof=1`) of high vs low over the window. | parity vs rolling cov. |
| `r_squared` | ✅ | square of the Pearson correlation between close and a straight time line. | parity. |
| `stderr` | ✅ | regression standard error `sqrt(Σresid²/(length-2))` (ddof=2); documented as distinct from pandas-ta's `stdev/√length`. | parity. |
| `tos_stdevall` | ✅ | ThinkOrSwim StDevAll: full-series linear regression + ±1/2/3σ residual bands. | parity vs `pandas_ta.tos_stdevall`. |

## cycle (9)

| Indicator | Verdict | Source review | Test review |
|---|---|---|---|
| `ht_dcperiod` | ✅ | Hilbert Transform dominant-cycle period via the shared `_hilbert.py` state machine (HT_START_32 warm-up, `mask_lookback`). | parity vs `talib.HT_DCPERIOD`. |
| `ht_dcphase` | ✅ | dominant-cycle phase (HT_START_63 warm-up). | parity vs `talib.HT_DCPHASE`. |
| `ht_phasor` | ✅ | in-phase / quadrature components from the same Hilbert pipeline. | parity vs `talib.HT_PHASOR`. |
| `ht_sine` | ✅ | sine / lead-sine from the dominant-cycle phase. | parity vs `talib.HT_SINE`. |
| `ht_trendmode` | ✅ | trend-vs-cycle mode flag (0/1). | parity vs `talib.HT_TRENDMODE`. |
| `ht_trendline` | ✅ | instantaneous trendline. | parity vs `talib.HT_TRENDLINE`. |
| `ebsw` | ✅ | Ehlers Even Better Sinewave — a standalone cycle oscillator (not the HT homodyne pipeline). | parity vs `pandas_ta.ebsw`. |
| `dsp` | ✅ | Detrended Synthetic Price = `close - EMA(close, length)` (talib-compatible SMA seed), matching pandas-ta-classic. | parity vs `pandas_ta.dsp`. |
| `msw` | ✅ | Mesa Sine Wave (the simpler sine/lead pair, not the homodyne HT pipeline). | parity vs reference. |

## Cross-cutting
- **Causality:** crossings and decays use only prior bars (`shift`); the Hilbert family carries a
  fixed 32/63-bar lookback warm-up. The real-data prefix-vs-full invariant test confirms no
  look-ahead across all 24.
