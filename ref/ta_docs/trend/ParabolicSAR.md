# Parabolic SAR — Stop and Reverse

- **Category:** trend
- **Author:** J. Welles Wilder, *New Concepts in Technical Trading Systems* (1978)
- **Defaults:** AF start 0.02, step 0.02, max 0.20

## 1. What it measures
A trailing stop that accelerates toward price over time, producing dots above (downtrend) or below (uptrend) price and a reversal when price crosses it.

## 2. How it works
Each bar the SAR moves toward the Extreme Point (EP) by an Acceleration Factor (AF) that increases every time a new EP is set, so the stop tightens faster the longer the trend runs.

## 3. Algorithm & formula
```
SAR_{t+1} = SAR_t + AF * (EP - SAR_t)
EP   = highest high so far (uptrend) / lowest low so far (downtrend)
AF   = starts 0.02, +0.02 each new EP, capped at 0.20
On flip: SAR resets to prior EP; AF -> 0.02; EP -> current extreme; trend reverses.
Clamp: SAR may not penetrate the prior two bars' price range.
```

## 4. Parameters / best settings
- `af_start=0.02, af_step=0.02, af_max=0.20` (Wilder). Lower step = fewer flips.
- TA-Lib `SAREXT` exposes separate long/short start values and offset-on-reverse.

## 5. Outputs & interpretation
Dots; trend = side of price the dots sit on; cross = stop-and-reverse signal.

## 6. Edge cases
- **Initialization:** needs an initial trend guess + seed SAR/EP from the first two bars.
- **Clamping rule** is mandatory and frequently omitted.

## 7. Pitfalls
- Omitting the two-bar penetration clamp produces stops inside the current candle.
- Performs poorly / whipsaws in sideways markets.

## 8. References & libraries
- TA-Lib `SAR`, `SAREXT`; pandas-ta `psar`; tulip `psar`; finta `PSAR`.
