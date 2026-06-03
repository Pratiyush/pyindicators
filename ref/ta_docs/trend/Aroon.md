# Aroon & Aroon Oscillator

- **Category:** trend
- **Author:** Tushar Chande (1995)
- **Default:** period 25

## 1. What it measures
How recently the highest high / lowest low occurred within the lookback — i.e. how "fresh" the trend is.

## 2. How it works
Counts bars since the period high (Aroon Up) and period low (Aroon Down).

## 3. Algorithm & formula
```
AroonUp   = 100 * (N - bars_since_highest_high) / N
AroonDown = 100 * (N - bars_since_lowest_low)  / N
AroonOsc  = AroonUp - AroonDown      # range -100..+100
```

## 4. Parameters / best settings
- `N=25` (Chande). 14 for faster.

## 5. Outputs & interpretation
- Up near 100 / Down near 0 = strong uptrend (and vice versa). Osc > 0 bullish.
- Both low = consolidation.

## 6. Edge cases
- **Tie** (high equals an earlier high) → define "most recent" vs "first" occurrence; document it.
- "Include current bar" affects `bars_since` (0 vs 1 indexing).

## 7. Pitfalls
- Off-by-one in `bars_since` is the dominant bug; libraries disagree on whether the window is N or N+1 bars.

## 8. References & libraries
- TA-Lib `AROON`, `AROONOSC`; pandas-ta `aroon`; tulip `aroon`/`aroonosc`; bukosabino/ta `AroonIndicator`.
