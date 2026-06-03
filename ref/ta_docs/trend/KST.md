# KST — Know Sure Thing (Pring's Summed ROC)

- **Category:** trend / momentum
- **Author:** Martin Pring
- **Defaults:** ROC 10/15/20/30, SMA 10/10/10/15, signal 9

## 1. What it measures
A smoothed, weighted sum of four Rate-of-Change values across different horizons — a long-term momentum oscillator.

## 2. How it works
Smooth each ROC with an SMA, weight them 1–4, sum, then add a signal line.

## 3. Algorithm & formula
```
RCMA1 = SMA(ROC(10), 10)   # weight 1
RCMA2 = SMA(ROC(15), 10)   # weight 2
RCMA3 = SMA(ROC(20), 10)   # weight 3
RCMA4 = SMA(ROC(30), 15)   # weight 4
KST    = 1*RCMA1 + 2*RCMA2 + 3*RCMA3 + 4*RCMA4
Signal = SMA(KST, 9)
```

## 4. Parameters / best settings
- Pring's defaults above (daily). A "long-term" monthly variant exists.

## 5. Outputs & interpretation
- Zero-line and signal crossovers; divergence.

## 6. Edge cases
- Long warmup (longest ROC + its SMA).

## 7. Pitfalls
- Getting the four ROC/SMA pairings or weights wrong.

## 8. References & libraries
- pandas-ta `kst`; finta `KST`; bukosabino/ta `KSTIndicator`. (Not in core TA-Lib.)
