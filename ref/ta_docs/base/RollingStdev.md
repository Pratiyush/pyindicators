# Rolling Standard Deviation / Variance

- **Category:** base / statistics primitive
- **Aliases:** STDDEV, VAR, moving stdev

## 1. What it measures
The dispersion of the last `N` values around their mean. Base component for Bollinger Bands, z-score, Relative Volatility Index, and many statistics functions.

## 2. How it works
Computes mean and mean-of-squares over a rolling window.

## 3. Algorithm & formula
```
mean_t = SMA(P, N)
var_t  = ( sum_{k=0}^{N-1} (P_{t-k} - mean_t)^2 ) / D
std_t  = sqrt(var_t)
```
- **Population:** `D = N` (TA-Lib `STDDEV`/`VAR` use population).
- **Sample:** `D = N - 1` (pandas `rolling().std()` defaults to `ddof=1`, i.e. sample).
TA-Lib `STDDEV` also accepts an `nbdev` multiplier (output = `nbdev * std`).

## 4. Parameters / best settings
- `length` (N): 20 (Bollinger). `ddof`: choose and document (default population to match TA-Lib).

## 5. Outputs & interpretation
Non-negative; higher = more volatile window.

## 6. Edge cases
- **Constant series:** variance = 0 → downstream division (e.g. %B, z-score) must guard against /0.
- **N=1:** sample stdev undefined (`D=0`); population stdev = 0.
- **Catastrophic cancellation:** the `E[x^2]-E[x]^2` shortcut loses precision; prefer a two-pass or Welford computation.

## 7. Pitfalls
- Population vs sample mismatch is a frequent cause of Bollinger Bands differing between libraries.

## 8. References & libraries
- TA-Lib `STDDEV`, `VAR`; pandas-ta `stdev`, `variance`; tulip `stddev`, `var`.
