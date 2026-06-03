# ATR / NATR — Average True Range (and Normalized)

- **Category:** volatility
- **Author:** J. Welles Wilder (1978)
- **Default:** period 14

## 1. What it measures
The average size of a bar's true range — a pure volatility measure (no direction). Base component for Supertrend, Keltner, Chandelier, position sizing.

## 2. How it works / formula
```
TR  = max(High-Low, |High-Close_{t-1}|, |Low-Close_{t-1}|)
ATR = Wilder-RMA(TR, N)        # first ATR = simple mean of first N TRs
NATR = 100 * ATR / Close
```

## 3. Parameters / best settings
- `N=14` (Wilder). Some use EMA or SMA smoothing — **document which**.

## 4. Outputs & interpretation
- Higher = more volatile; used for stops (e.g. 2–3×ATR) and sizing, not direction.

## 5. Edge cases
- **First TR** = High - Low (no prior close).
- **Flat series** → ATR = 0 (NATR fine unless Close = 0).

## 6. Pitfalls
- Wilder RMA vs EMA vs SMA produces different ATR — the usual "doesn't match" cause.

## 7. References & libraries
- TA-Lib `ATR`, `NATR`, `TRANGE`; pandas-ta `atr`, `natr`; tulip `atr`; bukosabino/ta `AverageTrueRange`.
