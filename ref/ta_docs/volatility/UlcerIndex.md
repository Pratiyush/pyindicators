# Ulcer Index

- **Category:** volatility (downside risk)
- **Author:** Peter Martin (1987)
- **Default:** period 14

## 1. What it measures
Depth and duration of drawdowns — a downside-only volatility/"pain" measure.

## 2. How it works / formula
```
R  = 100 * (Close - MaxClose(N)) / MaxClose(N)   # percent drawdown, <= 0
UI = sqrt( mean( R^2, N ) )
```

## 3. Parameters / best settings
- `N=14` (charting) or 14-of-period for fund analysis.

## 4. Outputs & interpretation
- Higher = deeper/longer drawdowns; used in the Martin (Ulcer Performance) ratio.

## 5. Edge cases
- **MaxClose = 0** → guard /0 (non-positive prices only).

## 6. Pitfalls
- Squaring only the negative drawdowns (R is already ≤ 0; square captures magnitude).

## 7. References & libraries
- pandas-ta `ui`; bukosabino/ta `UlcerIndex`. (Not in core TA-Lib.)
