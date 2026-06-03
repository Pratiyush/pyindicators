# SMA — Simple Moving Average

- **Category:** base / overlap
- **Aliases:** Moving Average, MA, Arithmetic MA

## 1. What it measures
The unweighted mean of the last `N` prices. It is the most basic smoothing operator and the building block for many other indicators (Bollinger Bands middle band, TRIMA, Stochastic %D, Chaikin Money Flow window, etc.).

## 2. How it works
Slides a fixed-width window of length `N` across the series and averages the values inside it. Every value in the window has equal weight `1/N`.

## 3. Algorithm & formula
```
SMA_t = (P_t + P_{t-1} + ... + P_{t-N+1}) / N
```
Efficient incremental form (O(1) per bar):
```
SMA_t = SMA_{t-1} + (P_t - P_{t-N}) / N
```
- First valid output is at index `N-1`. Indices `0 .. N-2` are NaN (warmup).

## 4. Parameters / best settings
- `length` (N): default 20. Common: 10, 20, 50, 100, 200.
- 50/200 SMA crossovers ("golden/death cross") are widely used on daily charts.

## 5. Outputs & interpretation
Single line. Price above SMA = uptrend bias; below = downtrend bias. Slope indicates trend direction. Crossovers between two SMAs of different length generate signals.

## 6. Edge cases
- **Warmup:** first `N-1` values are NaN; do not emit a partial average unless `min_periods < N` is explicitly requested.
- **Incremental drift:** the O(1) recurrence accumulates floating-point error over long series; prefer a windowed sum or periodic recomputation for very long inputs.
- **NaN inside window:** a single NaN poisons the window; decide whether to skip or propagate (default: propagate).

## 7. Pitfalls
- Equal weighting means SMA lags more than EMA for the same `N`.
- "Dropping" effect: SMA can jump when an old extreme value leaves the window even if the new price is unremarkable.

## 8. References & libraries
- TA-Lib `SMA` (Overlap Studies); pandas-ta `sma`; tulip `sma`; finta `SMA`; bukosabino/ta `SMAIndicator`.
