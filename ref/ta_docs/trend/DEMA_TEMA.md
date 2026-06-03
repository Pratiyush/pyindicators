# DEMA & TEMA — Double / Triple Exponential Moving Average

- **Category:** trend / overlap (low-lag EMA compositions)
- **Author:** Patrick Mulloy (1994)
- **Default:** period 20

## 1. What it measures
Reduced-lag smoothing built from nested EMAs. Not literally an N-times EMA — a lag-cancelling combination.

## 2. How it works
Compute EMA of EMA (and EMA of that), then combine so the smoothing lag partially cancels.

## 3. Algorithm & formula
```
e1 = EMA(price, N); e2 = EMA(e1, N); e3 = EMA(e2, N)
DEMA = 2*e1 - e2
TEMA = 3*e1 - 3*e2 + e3
```

## 4. Parameters / best settings
- `N=20` typical; smaller for faster signals.

## 5. Outputs & interpretation
Single low-lag line; reacts faster than EMA but overshoots more.

## 6. Edge cases
- **Warmup is long:** nested EMAs compound the warmup (~2N / 3N bars).
- Inherits the base EMA seeding convention through every layer.

## 7. Pitfalls
- Cannot be made by simply lowering N on a single EMA — the lag-cancel combination is the point.

## 8. References & libraries
- TA-Lib `DEMA`, `TEMA`; pandas-ta `dema`, `tema`; tulip `dema`, `tema`; finta `DEMA`, `TEMA`.
