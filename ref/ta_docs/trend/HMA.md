# HMA — Hull Moving Average

- **Category:** trend / overlap (low-lag)
- **Author:** Alan Hull (2005)
- **Default:** period 16 (also 9, 20, 49)

## 1. What it measures
A very low-lag, smooth moving average built from weighted MAs.

## 2. How it works
Combine a half-length WMA (fast) with a full-length WMA (slow) to cancel lag, then smooth the result with a WMA of length sqrt(N).

## 3. Algorithm & formula
```
HMA(N) = WMA( 2*WMA(price, N/2) - WMA(price, N), round(sqrt(N)) )
```
- `N/2` is integer-floored; `round(sqrt(N))` is the final smoothing length.

## 4. Parameters / best settings
- `N=16` common; trend-followers use 49–55, fast traders 9.

## 5. Outputs & interpretation
Smooth, responsive line; slope changes flag trend turns earlier than EMA.

## 6. Edge cases
- **Warmup:** `N + round(sqrt(N))` bars.
- Requires a correct **WMA** base (weights, direction).

## 7. Pitfalls
- Using EMA instead of WMA inside breaks the lag-cancelling property.
- `2*WMA(N/2) - WMA(N)` can exceed the price range briefly (overshoot).

## 8. References & libraries
- pandas-ta `hma`; finta `HMA`; freqtrade/technical `tv_hma`. (Not in core TA-Lib.)
