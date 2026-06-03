# Fisher Transform

- **Category:** momentum oscillator
- **Author:** John Ehlers
- **Default:** period 9

## 1. What it measures
Sharpens turning points by transforming price into an approximately Gaussian distribution, making extremes stand out.

## 2. How it works / formula
```
mid = (High + Low) / 2
X   = normalize mid to [-1, 1] over the N-period high/low range
X   = clamp(X, -0.999, 0.999)          # mandatory
Fish_t = 0.5*ln((1+X)/(1-X)) + 0.5*Fish_{t-1}   # with EMA-like smoothing
Trigger = Fish_{t-1}
```

## 3. Parameters / best settings
- `N=9` (also 10). 

## 4. Outputs & interpretation
- Sharp peaks = reversals; Fisher/Trigger crossovers; ±1.5/±2 extremes.

## 5. Edge cases
- **Must clamp X strictly inside ±1** or `ln` diverges to infinity (the #1 bug).
- **HH=LL** over window → X = 0.

## 6. Pitfalls
- Skipping the clamp; wrong normalization window.

## 7. References & libraries
- pandas-ta `fisher`; freqtrade/technical. (Not in core TA-Lib.)
