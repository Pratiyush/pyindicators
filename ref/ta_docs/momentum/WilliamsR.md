# Williams %R

- **Category:** momentum oscillator
- **Author:** Larry Williams
- **Default:** period 14

## 1. What it measures
Same idea as Stochastic %K but inverted and scaled -100..0: where the close sits in the recent range.

## 2. How it works / formula
```
%R = -100 * (HH(N) - Close) / (HH(N) - LL(N))
```

## 3. Parameters / best settings
- `N=14`. Bands: -20 overbought, -80 oversold.

## 4. Outputs & interpretation
- 0 = close at the top of range; -100 = bottom. Reversals near extremes.

## 5. Edge cases
- **HH=LL** → guard /0.

## 6. Pitfalls
- Sign/scale confusion (it is negative, 0 at top).

## 7. References & libraries
- TA-Lib `WILLR`; pandas-ta `willr`; tulip `willr`; bukosabino/ta `WilliamsRIndicator`.
