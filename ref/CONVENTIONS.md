# Library-Wide Conventions (read before implementing any indicator)

## Per-file documentation template (every indicator .md uses these 10 sections)
1. Name & aliases  2. Category  3. What it measures  4. How it works
5. Algorithm & formula (with initialization/seeding)  6. Parameters / best settings
7. Outputs & interpretation  8. Edge cases  9. Pitfalls  10. References & libraries

## Class design
- One abstract `Indicator` base class: validates OHLCV input schema, validates parameters, enforces a uniform NaN/warmup policy, exposes the shared base components.
- **One class per indicator.** Never reimplement EMA/ATR/RMA/stdev inline — always compose from `base/`.
- A single `MovingAverage` dispatcher so any indicator can swap MA type
  (TA-Lib MA-type codes: 0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3).
- Add a `talib_compatible` flag wherever seeding/smoothing conventions differ from pandas defaults.

## Universal edge-case policy (standardize once, not per indicator)
- **Division by zero:** guard every ratio. Constant/flat series make range (H-L), TR, summed gains/losses, and stdev zero.
  - RSI: AvgLoss=0 → 100; AvgGain=0 → 0; both 0 → carry prior (TA-Lib).
  - Stochastic/Williams %R: HH=LL → %K undefined → 0/50/forward-fill (document).
  - CMF/Money-Flow Multiplier: H=L → multiplier = 0 (NOT NaN).
  - Fisher: clamp normalized value strictly inside ±1 or ln diverges.
- **Warmup / insufficient lookback:** first N-1 bars of an N-window are NaN. EMA seeding differs:
  TA-Lib seeds EMA with SMA of first N (valid at index N-1); pandas `ewm(adjust=False)` seeds with first value (valid at 0).
- **NaN handling:** decide propagate vs skip and apply consistently; `min_periods == window` unless deliberately relaxed.
- **Gaps / sessions:** True Range captures gaps via prior close; VWAP must reset per session (needs DatetimeIndex).
- **Unstable period:** ADX needs ~150 bars; Hilbert Transform family needs 32–63 fixed bars + optional unstable period (raisable ~100).

## Build order (dependency-driven)
1. **base/** — SMA, EMA, WMA, RMA, rolling stdev/variance, True Range (test to TA-Lib parity first).
2. **Tier 2** — ATR, MACD, Bollinger, Stochastic, RSI, ADX/DMI, DEMA/TEMA/T3, KAMA, HMA, Supertrend, Keltner, Donchian, Chandelier.
3. **Tier 3 (composites)** — StochRSI, Connors RSI, Schaff Trend Cycle, Chaikin Osc, TSI, KST, Ichimoku (with lookahead flag), Hilbert family.
4. **Breadth** — remaining oscillators, volume, statistics, candlesticks, math transforms.

## Testing
- Compare against TA-Lib and pandas-ta where overlap exists; pin expected divergences (EMA seeding, population vs sample stdev, Wilder vs SMA in RSI). Target floating-point parity (<1e-6) for base + tier-2.
