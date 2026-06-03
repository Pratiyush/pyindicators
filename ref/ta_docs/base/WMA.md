# WMA — Weighted Moving Average

- **Category:** base / overlap
- **Aliases:** Linearly Weighted Moving Average, LWMA

## 1. What it measures
A moving average where weights decline linearly from the most recent bar to the oldest, putting more emphasis on recent prices than SMA but using a finite window (unlike EMA).

## 2. How it works
The most recent price gets weight `N`, the next `N-1`, down to `1` for the oldest. Divide by the triangular number `N(N+1)/2`.

## 3. Algorithm & formula
```
WMA_t = (N*P_t + (N-1)*P_{t-1} + ... + 1*P_{t-N+1}) / (N + (N-1) + ... + 1)
       = sum_{k=0}^{N-1} (N-k) * P_{t-k} / (N(N+1)/2)
```
First valid output at index `N-1`.

## 4. Parameters / best settings
- `length` (N): default 9 or 20. WMA(period) is the core component of HMA.

## 5. Outputs & interpretation
Single line; less lag than SMA, less smooth than EMA at equal N.

## 6. Edge cases
- **Warmup:** first `N-1` NaN.
- Denominator `N(N+1)/2` is constant and never zero for `N>=1`.

## 7. Pitfalls
- Reversing the weight direction (oldest heaviest) is a common bug.
- Confusing WMA with VWMA (volume-weighted) — different concept.

## 8. References & libraries
- TA-Lib `WMA`; pandas-ta `wma`; tulip `wma`; finta `WMA`.
