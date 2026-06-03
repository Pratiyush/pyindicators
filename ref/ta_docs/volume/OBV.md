# OBV — On-Balance Volume

- **Category:** volume
- **Author:** Joe Granville (1963)

## 1. What it measures
A running total of volume added on up-closes and subtracted on down-closes — cumulative buying/selling pressure.

## 2. How it works / formula
```
OBV_t = OBV_{t-1} + ( +Volume_t if Close_t > Close_{t-1}
                      -Volume_t if Close_t < Close_{t-1}
                       0        if equal )
```
Seed `OBV_0 = 0` (or first volume — document).

## 3. Parameters / best settings
- None. Often paired with its own MA for signals.

## 4. Outputs & interpretation
- OBV trend confirms price trend; OBV/price divergence warns of reversal.

## 5. Edge cases
- **Unchanged close** adds 0.
- Absolute level is arbitrary (depends on seed) — only the trend matters.

## 6. Pitfalls
- Comparing absolute OBV across instruments (meaningless).

## 7. References & libraries
- TA-Lib `OBV`; pandas-ta `obv`; tulip `obv`; bukosabino/ta `OnBalanceVolumeIndicator`.
