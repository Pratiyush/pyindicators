# Ultimate Oscillator (UO)

- **Category:** momentum oscillator
- **Author:** Larry Williams (1976)
- **Defaults:** 7, 14, 28 (weights 4, 2, 1)

## 1. What it measures
Momentum across three timeframes combined to reduce the false divergences single-period oscillators suffer.

## 2. How it works / formula
```
BP = Close - min(Low, Close_{t-1})                 # buying pressure
TR = max(High, Close_{t-1}) - min(Low, Close_{t-1})
Avg_n = sum(BP, n) / sum(TR, n)
UO = 100 * (4*Avg7 + 2*Avg14 + Avg28) / (4 + 2 + 1)
```

## 3. Parameters / best settings
- 7/14/28, weights 4/2/1 (Williams).

## 4. Outputs & interpretation
- 0–100; >70 overbought, <30 oversold; primary use is divergence.

## 5. Edge cases
- **sum(TR)=0** only on flat-no-gap data → guard /0.

## 6. Pitfalls
- BP/TR use prior close (not just intrabar range).

## 7. References & libraries
- TA-Lib `ULTOSC`; pandas-ta `uo`; bukosabino/ta `UltimateOscillator`.
