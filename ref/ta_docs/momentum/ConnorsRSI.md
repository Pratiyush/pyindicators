# Connors RSI (CRSI)

- **Category:** momentum oscillator (composite)
- **Author:** Larry Connors
- **Defaults:** RSI 3, Streak-RSI 2, PercentRank 100

## 1. What it measures
A mean-reversion oscillator blending price RSI, a short RSI of the up/down *streak*, and the percentile rank of the 1-day return.

## 2. How it works / formula
```
A = RSI(Close, 3)
streak = consecutive count of up(+) / down(-) closes; 0 if unchanged
B = RSI(streak, 2)
C = PercentRank( ROC(Close,1), 100 )   # % of last 100 returns below today's
CRSI = (A + B + C) / 3
```

## 3. Parameters / best settings
- 3/2/100 (Connors). Bands 90/10 (some 95/5).

## 4. Outputs & interpretation
- 0–100; extreme highs/lows flag short-term reversals.

## 5. Edge cases
- **Streak resets to 0** on an unchanged close.
- PercentRank needs the full 100-bar window before it's valid.

## 6. Pitfalls
- Applying RSI to **price** for the 2nd term (it must be applied to the streak series).

## 7. References & libraries
- pandas-ta `crsi`/`cti`? — implemented in pandas-ta-classic; finta has components. (Not in core TA-Lib.)
