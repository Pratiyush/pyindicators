# PPO — Percentage Price Oscillator

- **Category:** trend / momentum
- **Default:** fast 12, slow 26, signal 9

## 1. What it measures
MACD expressed in **percentage** terms, so it is comparable across instruments of different price levels.

## 2. How it works
Same as MACD but normalized by the slow EMA.

## 3. Algorithm & formula
```
PPO    = 100 * (EMA(close, fast) - EMA(close, slow)) / EMA(close, slow)
Signal = EMA(PPO, signal)
Hist   = PPO - Signal
```

## 4. Parameters / best settings
- 12/26/9 (classic). APO is the same but **non-normalized** (absolute).

## 5. Outputs & interpretation
- Like MACD: signal crosses, zero-line, divergence — but percentage units allow cross-asset comparison.

## 6. Edge cases
- **Slow EMA = 0** → guard /0 (degenerate data only).

## 7. Pitfalls
- Confusing PPO (percentage) with APO (absolute).

## 8. References & libraries
- TA-Lib `PPO`, `APO`; pandas-ta `ppo`, `apo`; tulip `ppo`; bukosabino/ta `PercentagePriceOscillator`.
