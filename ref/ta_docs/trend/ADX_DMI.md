# ADX / DMI — Average Directional Index & Directional Movement

- **Category:** trend (strength + direction)
- **Author:** J. Welles Wilder (1978)
- **Components:** +DI, -DI, DX, ADX, ADXR
- **Default:** period 14

## 1. What it measures
**DMI** (+DI/-DI) shows directional movement; **ADX** measures trend *strength* regardless of direction.

## 2. How it works
Derive directional movement (+DM/-DM) from consecutive highs/lows, Wilder-smooth them and TR, ratio to get +DI/-DI, then smooth their normalized spread into ADX.

## 3. Algorithm & formula
```
upMove   = High_t - High_{t-1}
downMove = Low_{t-1} - Low_t
+DM = upMove   if (upMove > downMove and upMove > 0)   else 0
-DM = downMove if (downMove > upMove and downMove > 0) else 0
TR  = true range
# Wilder-smooth +DM, -DM, TR over N (sum-seed):
Smoothed_t = Smoothed_{t-1} - Smoothed_{t-1}/N + Current_t
+DI = 100 * Smoothed(+DM) / Smoothed(TR)
-DI = 100 * Smoothed(-DM) / Smoothed(TR)
DX  = 100 * abs(+DI - -DI) / (+DI + -DI)
ADX = Wilder-RMA(DX, N)            # first ADX = mean of first N DX values
ADXR = (ADX_t + ADX_{t-N}) / 2
```

## 4. Parameters / best settings
- `period=14`. ADX > 25 = trending; < 20 = weak/no trend (Wilder). Some use 20/25 bands.

## 5. Outputs & interpretation
- +DI crossing above -DI = bullish; below = bearish.
- Rising ADX = strengthening trend (either direction); falling ADX = weakening.

## 6. Edge cases
- **Inside bars** (both moves <=0) → +DM = -DM = 0.
- **+DI + -DI = 0** → DX = 0 (guard /0).
- **Warmup:** ~150 bars for ADX to fully stabilize due to double smoothing.

## 7. Pitfalls
- Sum-seed vs mean-seed and the two-stage smoothing are the main cross-library mismatches.
- ADX gives no direction — must be paired with +DI/-DI or price.

## 8. References & libraries
- TA-Lib `ADX`, `ADXR`, `DX`, `PLUS_DI`, `MINUS_DI`, `PLUS_DM`, `MINUS_DM`; pandas-ta `adx`; tulip `adx`/`di`/`dm`; bukosabino/ta `ADXIndicator`. StockCharts ChartSchool is canonical.
