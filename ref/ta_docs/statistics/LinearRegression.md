# Linear Regression Family (linreg, slope, intercept, angle, TSF, R²)

- **Category:** statistics
- **Default:** period 14

## 1. What it measures
Least-squares line fit over a rolling window; outputs the fitted endpoint, slope, intercept, angle, forecast, and goodness-of-fit.

## 2. How it works / formula
For window of N points (x = 0..N-1):
```
slope     = ( N*sum(x*y) - sum(x)*sum(y) ) / ( N*sum(x^2) - sum(x)^2 )
intercept = ( sum(y) - slope*sum(x) ) / N
linreg    = intercept + slope*(N-1)          # value at window end
TSF       = intercept + slope*N              # 1-step forecast
angle     = atan(slope) in degrees
R2        = correlation(x, y)^2
```

## 3. Parameters / best settings
- `N=14`. LSMA (Least Squares MA) = the `linreg` endpoint series.

## 4. Outputs & interpretation
- Slope sign/steepness = trend direction/strength; R² = trend reliability.

## 5. Edge cases
- Denominator `N*sum(x^2)-sum(x)^2` is constant > 0 for N>1 (no /0 with fixed x).
- Warmup N bars.

## 6. Pitfalls
- Endpoint convention: value at `x=N-1` (linreg) vs `x=N` (TSF) — off-by-one.

## 7. References & libraries
- TA-Lib `LINEARREG`, `LINEARREG_SLOPE`, `LINEARREG_INTERCEPT`, `LINEARREG_ANGLE`, `TSF`; pandas-ta `linreg`; tulip `linreg`,`linregslope`,`linregintercept`,`tsf`.
