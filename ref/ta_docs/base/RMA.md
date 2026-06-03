# RMA — Wilder's Smoothing (a.k.a. SMMA, Wilder's MA, Modified MA)

- **Category:** base / overlap
- **Aliases:** SMMA (Smoothed Moving Average), Wilder's Smoothing, Modified Moving Average (MMA), Running Moving Average

## 1. What it measures
The smoothing operator J. Welles Wilder used throughout his indicators (RSI, ATR, ADX/DMI). It is mathematically an EMA with `alpha = 1/N` instead of `2/(N+1)`, so it is much "slower" than a same-period EMA.

## 2. How it works
Like EMA but with a smaller smoothing factor, and with a specific seeding rule: the first value is the simple average (or sum, depending on the indicator) of the first `N` inputs.

## 3. Algorithm & formula
```
alpha = 1 / N        # equivalently RMA(N) ~ EMA(2N-1)
First value: RMA_{N-1} = mean(P_0 .. P_{N-1})    # (RSI/ATR style)
Then:        RMA_t = (RMA_{t-1} * (N-1) + P_t) / N
                   = RMA_{t-1} + (P_t - RMA_{t-1}) / N
```
Some Wilder indicators seed with a **sum** (not mean) and use:
`Smoothed_t = Smoothed_{t-1} - Smoothed_{t-1}/N + Current_t` — used for +DM/-DM/TR in ADX.

## 4. Parameters / best settings
- `length` (N): inherited from the parent indicator (14 for RSI/ATR/ADX).

## 5. Outputs & interpretation
Internal smoothing line; rarely plotted alone. Determines the "feel" of RSI/ATR/ADX.

## 6. Edge cases
- **Seeding** (mean vs sum) must match the parent indicator's definition exactly.
- **Warmup:** ADX needs ~150 bars before RMA-of-RMA stabilizes.

## 7. Pitfalls
- Using a standard EMA (`alpha=2/(N+1)`) in place of RMA gives noticeably different RSI/ATR/ADX values — this is the classic "my RSI doesn't match TradingView" bug.
- Mixing the mean-seed and sum-seed variants.

## 8. References & libraries
- pandas-ta `rma`; tulip `wilders`; TA-Lib applies it internally inside RSI/ATR/ADX; bukosabino/ta uses it inside RSI/ATR.
