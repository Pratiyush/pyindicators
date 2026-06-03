# Supertrend

- **Category:** trend / overlap (uses ATR)
- **Author:** Olivier Seban (~2009)
- **Defaults:** ATR period 10, multiplier 3

## 1. What it measures
A trailing stop / trend-direction line built from ATR. Tells you the current trend side and a dynamic stop level.

## 2. How it works
Places bands a multiple of ATR above/below the median price, then applies a carry-forward rule so the active band only tightens (never loosens against you) until price closes through it, flipping the trend.

## 3. Algorithm & formula
```
hl2        = (High + Low) / 2
BasicUpper = hl2 + mult * ATR(period)
BasicLower = hl2 - mult * ATR(period)

FinalUpper_t = BasicUpper_t  if (BasicUpper_t < FinalUpper_{t-1}) or (Close_{t-1} > FinalUpper_{t-1})
               else FinalUpper_{t-1}
FinalLower_t = BasicLower_t  if (BasicLower_t > FinalLower_{t-1}) or (Close_{t-1} < FinalLower_{t-1})
               else FinalLower_{t-1}

Supertrend flips:
  if prev line was Upper and Close > FinalUpper -> switch to Lower (uptrend, dir=+1)
  if prev line was Lower and Close < FinalLower -> switch to Upper (downtrend, dir=-1)
```

## 4. Parameters / best settings
- Scalping: ATR 7, mult 2. Swing: ATR 14, mult 4. Default 10/3 for general use.
- ATR may use Wilder RMA or EMA — **document which**.

## 5. Outputs & interpretation
- Line + direction (+1/-1). Price above line = long; flip below = exit/short.

## 6. Edge cases
- **Warmup:** needs ATR warmup; first bars undefined.
- **Stateful:** the carry-forward is iterative — cannot be fully vectorized without care.

## 7. Pitfalls
- Implementations differ in the exact carry-forward and flip conditions — pick one and pin it with tests.
- Whipsaws in ranging markets; not a standalone system.

## 8. References & libraries
- pandas-ta `supertrend`; freqtrade/technical; many TradingView ports. LiteFinance/FBS have readable formula write-ups.
