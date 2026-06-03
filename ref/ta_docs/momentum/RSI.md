# RSI — Relative Strength Index

- **Category:** momentum oscillator
- **Author:** J. Welles Wilder (1978)
- **Default:** period 14

## 1. What it measures
The speed and magnitude of recent gains vs losses, scaled 0–100.

## 2. How it works
Average the up-moves and down-moves with Wilder's smoothing, ratio them, map to 0–100.

## 3. Algorithm & formula
```
change   = close_t - close_{t-1}
gain     = max(change, 0);  loss = max(-change, 0)
AvgGain  = Wilder-RMA(gain, N)   # first = simple mean of first N gains
AvgLoss  = Wilder-RMA(loss, N)
RS       = AvgGain / AvgLoss
RSI      = 100 - 100 / (1 + RS)
```

## 4. Parameters / best settings
- `N=14` (Wilder). **RSI(2)** for mean-reversion (Connors). 9/21 also used.
- Bands: 70/30 standard; 80/20 in strong trends.

## 5. Outputs & interpretation
- >70 overbought, <30 oversold; centerline 50; divergence vs price.

## 6. Edge cases
- **AvgLoss = 0** → RS = ∞ → RSI = 100.
- **AvgGain = 0** → RSI = 0.
- **Both 0** (flat series) → convention; TA-Lib carries the prior value forward.

## 7. Pitfalls
- **Using SMA instead of Wilder's RMA** gives "Cutler's RSI" — different numbers and the classic "doesn't match TradingView" bug.
- Seeding the first average wrong (mean of first N vs running from bar 0).

## 8. References & libraries
- TA-Lib `RSI`; pandas-ta `rsi`; tulip `rsi`; finta `RSI`; bukosabino/ta `RSIIndicator`.
