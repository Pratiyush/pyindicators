# Bollinger Bands (+ %B, Bandwidth)

- **Category:** volatility / overlap
- **Author:** John Bollinger (1980s)
- **Defaults:** length 20, stdev multiplier 2

## 1. What it measures
A volatility envelope around an SMA; band width expands/contracts with volatility.

## 2. How it works / formula
```
Middle = SMA(close, 20)
Upper  = Middle + k * stdev(close, 20)     # k = 2, population stdev
Lower  = Middle - k * stdev(close, 20)
%B     = (Close - Lower) / (Upper - Lower)
Bandwidth = (Upper - Lower) / Middle
```

## 3. Parameters / best settings
- 20/2 (Bollinger). Some use 10/1.9 or 50/2.1. **Use population stdev to match TA-Lib.**

## 4. Outputs & interpretation
- Touches of bands = relative extremes; "squeeze" (low bandwidth) precedes expansion; %B locates price within the bands.

## 5. Edge cases
- **stdev = 0** (flat) → bands collapse to middle; **%B division by zero** → guard.
- Population vs sample stdev mismatch with other libraries.

## 6. Pitfalls
- Sample (ddof=1) vs population (ddof=0) stdev is the main cross-library discrepancy.

## 7. References & libraries
- TA-Lib `BBANDS`; pandas-ta `bbands`; finta `BBANDS`; bukosabino/ta `BollingerBands`.
