# MFI — Money Flow Index

- **Category:** volume ("volume-weighted RSI")
- **Default:** period 14

## 1. What it measures
RSI-like oscillator that incorporates volume via typical-price money flow.

## 2. How it works / formula
```
TP  = (High + Low + Close) / 3
RMF = TP * Volume                       # raw money flow
Positive/Negative MF based on TP vs TP_{t-1}
MoneyRatio = sum(PosMF, N) / sum(NegMF, N)
MFI = 100 - 100 / (1 + MoneyRatio)
```

## 3. Parameters / best settings
- `N=14`. Bands 80/20.

## 4. Outputs & interpretation
- >80 overbought, <20 oversold; divergence.

## 5. Edge cases
- **sum(NegMF)=0** → MFI = 100.
- **Unchanged TP** excluded from both sums.

## 6. Pitfalls
- Using close instead of typical price; mishandling unchanged TP.

## 7. References & libraries
- TA-Lib `MFI`; pandas-ta `mfi`; tulip `mfi`; bukosabino/ta `MFIIndicator`.
