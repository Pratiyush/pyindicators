# pyindicators — correctness audit (2026-06)

A four-way independent audit of every implemented indicator (146 at audit time), each
cross-checked against TA-Lib, pandas-ta-classic, finta and bukosabino-`ta` on **real AAPL daily
data** plus synthetic and edge frames, with the reference formulas re-derived from source rather
than trusting our own docstrings. Re-runnable any time via the review pipeline:

    uv run python scripts/audit_indicators.py        # robustness + causality + parity coverage

This file is the point-in-time narrative (methodology + the concerns table). For live, never-drift
numbers — how many indicators exist, which carry an individual `review`, and each one's
edge/parity/3-lib/real/invalid status — see the auto-generated `docs/TRACKING.md` (the single
source of truth) and re-run the pipeline above.

## Result: 0 bugs

| Category group | Indicators | Verified | Concerns | Bugs |
|----------------|-----------:|---------:|---------:|-----:|
| base / price_transform / statistics / relative / structure | 32 | 32 | 0 | 0 |
| trend | 45 | 42 | 3 | 0 |
| momentum | 36 | 35 | 1 | 0 |
| volatility / volume | 33 | 30 | 3 | 0 |
| **total** | **146** | **139** | **7** | **0** |

No wrong formulas, no look-ahead, no bound violations, no crashes on edge frames.

## The 7 concerns — all convention/scale, now resolved

Every concern was a place where our output equalled a *defensible canonical definition* but
diverged from a *cited* reference library by a constant factor or a smoother choice. Fixed by
aligning to the standard where one exists, else documenting the convention honestly.

| Indicator | Finding | Resolution |
|-----------|---------|------------|
| `bb_bandwidth` | ours `(U-L)/M`; pandas-ta/StockCharts/TradingView use `×100` | **aligned to ×100** (behavior + golden test) |
| `cmo` | claimed "TA-Lib CMO" + `talib_compatible=True`, but matches pandas-ta's simple-sum CMO (TA-Lib uses Wilder) | `talib_compatible=False`, references/docstring corrected |
| `trix` (signal) | line matches TA-Lib/pandas-ta exactly; signal is EMA(9) (StockCharts) vs pandas-ta SMA(9) | docstring states the signal convention |
| `kst` | matches StockCharts/`ta`; pandas-ta is 100× (non-standard) | docstring notes it; parity test already ÷100 |
| `pvt` | canonical StockCharts fractional form; pandas-ta is 100× | docstring notes it; parity test already ÷100 |
| `pvr` | bar 0 NaN (no prior); pandas-ta fills 0 → rank 1 there | docstring notes it; all later bars match |
| `alma` | deliberately matches canonical TradingView/Pine; pandas-ta reverses the weights | already documented (no change) |

## Standing review pipeline

`scripts/audit_indicators.py` runs three review stages over the whole registry and exits
non-zero on any hard failure (so it can gate a build):

1. **Robustness / edge** — constant, interior-NaN, 2-row and zero-volume frames must not crash,
   must preserve length, must not emit ±inf, and must respect declared bounds on real data.
2. **Causality** — no look-ahead (`compute(df[:k]) == compute(df)[:k]`), deterministic, no input
   mutation.
3. **Parity coverage** — flags any indicator lacking a parity test or a real-data test (the
   backfill list; not a hard failure).

Per-indicator detail for the foundation/stats group lives in
`ref/AUDIT_base_pricetransform_stats_relative_structure.md`.
