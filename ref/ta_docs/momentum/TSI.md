# TSI — True Strength Index

- **Category:** momentum oscillator
- **Author:** William Blau
- **Defaults:** long 25, short 13, signal 7

## 1. What it measures
Double-smoothed price momentum, normalized to roughly -100..+100.

## 2. How it works / formula
```
pc   = close - close_{t-1}
pcs  = EMA(pc, long);   pcds  = EMA(pcs, short)
apc  = abs(pc)
apcs = EMA(apc, long);  apcds = EMA(apcs, short)
TSI  = 100 * pcds / apcds
Signal = EMA(TSI, signal)
```

## 3. Parameters / best settings
- 25/13/7 (Blau). ±25 cutoffs common.

## 4. Outputs & interpretation
- Zero-line crosses, signal crosses, divergence.

## 5. Edge cases
- **apcds = 0** (flat) → guard /0.

## 6. Pitfalls
- Order of smoothing (long then short) matters; both numerator and denominator double-smoothed identically.

## 7. References & libraries
- pandas-ta `tsi`; bukosabino/ta `TSIIndicator`. (Not in core TA-Lib.)
