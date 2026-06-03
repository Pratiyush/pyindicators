# EMA — Exponential Moving Average

- **Category:** base / overlap
- **Aliases:** EWMA, Exponentially Weighted MA

## 1. What it measures
A moving average that weights recent prices exponentially more than older ones, giving faster response to new information than the SMA for the same period.

## 2. How it works
Each new value is a blend of the current price and the previous EMA, controlled by a smoothing factor `alpha`. Older prices never fully leave; their influence decays geometrically.

## 3. Algorithm & formula
```
alpha = 2 / (N + 1)
EMA_t = alpha * P_t + (1 - alpha) * EMA_{t-1}
```
**Seeding (CRITICAL — libraries differ):**
- **TA-Lib convention:** seed the first EMA with the SMA of the first `N` values; first valid output at index `N-1`.
- **pandas `ewm(span=N, adjust=False)` convention:** seed with the first price `P_0`; valid from index 0.
These produce different early values and small persistent differences. Pick one, document it, expose a `talib_compatible` flag.

## 4. Parameters / best settings
- `length` (N): defaults 9, 12, 20, 26, 50, 200. `alpha` may be overridden directly.

## 5. Outputs & interpretation
Single line. Faster crossovers than SMA. 12/26 EMA pair underlies MACD.

## 6. Edge cases
- **Seeding mismatch** (see above) is the #1 source of cross-library discrepancy.
- **Warmup:** with SMA-seed, first `N-1` are NaN.
- **Constant series:** EMA equals the constant (stable).

## 7. Pitfalls
- Reimplementing EMA inside other indicators with a different seed than your base EMA breaks internal consistency. Always compose from one EMA implementation.
- `adjust=True` in pandas gives a *different* (finite-sample-unbiased) weighting — not the recursive EMA most TA formulas assume. Use `adjust=False`.

## 8. References & libraries
- TA-Lib `EMA`; pandas-ta `ema`; tulip `ema`; finta `EMA`; bukosabino/ta `EMAIndicator`.
