# CCI — Commodity Channel Index

- **Category:** momentum oscillator
- **Author:** Donald Lambert (1980)
- **Default:** period 20, constant 0.015

## 1. What it measures
How far typical price is from its moving average, in units of mean absolute deviation.

## 2. How it works / formula
```
TP   = (High + Low + Close) / 3
CCI  = (TP - SMA(TP, N)) / (0.015 * MeanDeviation(TP, N))
MeanDeviation = mean(|TP_i - SMA(TP,N)|) over N
```

## 3. Parameters / best settings
- `N=20`, constant `0.015` (Lambert; calibrated so ~70–80% of values fall in ±100).

## 4. Outputs & interpretation
- Unbounded; >+100 strong up / overbought, <-100 strong down / oversold; zero-line crosses.

## 5. Edge cases
- **MeanDeviation = 0** (flat TP) → guard /0 → CCI = 0.

## 6. Pitfalls
- Using stdev instead of **mean absolute deviation**.
- Forgetting the 0.015 constant.

## 7. References & libraries
- TA-Lib `CCI`; pandas-ta `cci`; tulip `cci`; bukosabino/ta `CCIIndicator`.
