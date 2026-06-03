# KAMA — Kaufman's Adaptive Moving Average

- **Category:** trend / adaptive overlap
- **Author:** Perry J. Kaufman
- **Default:** KAMA(er=10, fast=2, slow=30)

## 1. What it measures
A moving average that automatically speeds up in trending markets and slows down (flattens) in noisy/sideways markets, using an Efficiency Ratio.

## 2. How it works
Measures how "efficient" recent movement is (net change vs total path length). High efficiency → behave like a fast EMA; low efficiency → behave like a slow EMA.

## 3. Algorithm & formula
```
Change     = abs(Close - Close_{t-n})                 # n = er period (10)
Volatility = sum(abs(Close_i - Close_{i-1}), n)
ER         = Change / Volatility                      # 0..1
fastest    = 2/(fast+1)   slowest = 2/(slow+1)        # fast=2, slow=30
SC         = (ER * (fastest - slowest) + slowest) ^ 2 # NOTE: squared
KAMA_t     = KAMA_{t-1} + SC * (Close - KAMA_{t-1})
```
Seed `KAMA` with the first close or an SMA at the warmup boundary.

## 4. Parameters / best settings
- `er=10, fast=2, slow=30` (Kaufman's defaults). Larger `er` = smoother ER.

## 5. Outputs & interpretation
Single adaptive line; flat KAMA = chop (stand aside), rising/falling sloped KAMA = trend.

## 6. Edge cases
- **Volatility = 0** (constant price) → ER undefined; set `ER=0` so `SC = slowest^2`.
- **Warmup:** first `er` bars NaN.

## 7. Pitfalls
- **Forgetting to square `SC`** is the most common implementation bug.
- Off-by-one on the `Change` lookback (`n` vs `n-1`).

## 8. References & libraries
- TA-Lib `KAMA`; pandas-ta `kama`; tulip `kama`; bukosabino/ta `KAMAIndicator`. StockCharts ChartSchool has the canonical worked example.
