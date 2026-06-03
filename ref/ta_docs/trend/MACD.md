# MACD — Moving Average Convergence Divergence

- **Category:** trend / momentum hybrid
- **Aliases:** MACD; components: MACD line, Signal line, Histogram
- **Author:** Gerald Appel (late 1970s)

## 1. What it measures
The relationship between two EMAs of price. Captures momentum and trend direction simultaneously.

## 2. How it works
Subtract a slow EMA from a fast EMA to get the MACD line; smooth that with another EMA to get the signal line; their difference is the histogram.

## 3. Algorithm & formula
```
MACD   = EMA(close, fast) - EMA(close, slow)      # fast=12, slow=26
Signal = EMA(MACD, signal_len)                     # signal=9
Hist   = MACD - Signal
```
- Depends on the **base EMA** (and its seeding convention). The signal EMA is seeded from the MACD line once it exists.

## 4. Parameters / best settings
- `fast=12, slow=26, signal=9` (classic). Faster intraday: 5/35/5. TA-Lib `MACDEXT` lets each leg pick an MA type; `MACDFIX` fixes 12/26.

## 5. Outputs & interpretation
- MACD crossing Signal up = bullish; down = bearish.
- Histogram above/below zero; histogram shrinking = momentum fading.
- MACD/zero-line crosses = longer-term trend shift. Divergence vs price = reversal warning.

## 6. Edge cases
- **Warmup:** needs slow + signal warmup before histogram is meaningful (~`slow + signal` bars).
- **EMA seeding** flows through to all three outputs — match your base EMA.

## 7. Pitfalls
- Comparing your MACD to a charting platform that uses a different EMA seed will show small persistent offsets.
- The histogram's "convergence/divergence" is relative to the signal line, not price.

## 8. References & libraries
- TA-Lib `MACD`, `MACDEXT`, `MACDFIX`; pandas-ta `macd`; tulip `macd`; finta `MACD`; bukosabino/ta `MACD`.
