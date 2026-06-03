# TRIX — Triple Exponential Average (rate of change)

- **Category:** trend / momentum oscillator
- **Author:** Jack Hutson (1980s)
- **Default:** period 15, signal 9

## 1. What it measures
The percentage rate of change of a triple-smoothed EMA — a slow, noise-filtered momentum oscillator centered on zero.

## 2. How it works
Triple-EMA the (log) price, then take its 1-bar percent change.

## 3. Algorithm & formula
```
e1 = EMA(price, N); e2 = EMA(e1, N); e3 = EMA(e2, N)
TRIX = 100 * (e3_t - e3_{t-1}) / e3_{t-1}
Signal = EMA(TRIX, signal_len)   # or SMA in some variants
```

## 4. Parameters / best settings
- `N=15` (classic), signal 9. Shorter N = more signals.

## 5. Outputs & interpretation
- Zero-line crosses = trend shifts; TRIX/signal crosses = entries; divergence vs price.

## 6. Edge cases
- **Division by `e3_{t-1}`** — guard if triple-EMA ever hits 0 (only on degenerate data).
- Long warmup (~3N).

## 7. Pitfalls
- Signal smoothing type (EMA vs SMA) differs across libraries.

## 8. References & libraries
- TA-Lib `TRIX`; pandas-ta `trix`; tulip `trix`; finta `TRIX`.
