# True Range (TR)

- **Category:** base / volatility primitive
- **Aliases:** TR

## 1. What it measures
The greatest of the day's range and the gaps to the prior close — a gap-aware measure of one bar's price movement. It is the input to ATR, NATR, Supertrend, Keltner, Chandelier, Ultimate Oscillator, Vortex, and more.

## 2. How it works
Takes the maximum of three candidate ranges so that overnight gaps are not understated.

## 3. Algorithm & formula
```
TR_t = max(
    High_t - Low_t,
    abs(High_t - Close_{t-1}),
    abs(Low_t  - Close_{t-1})
)
```
- First bar has no previous close: `TR_0 = High_0 - Low_0`.

## 4. Parameters / best settings
None (per-bar). Period is applied later by ATR.

## 5. Outputs & interpretation
A non-negative series; larger = more volatile/gappy bar.

## 6. Edge cases
- **First bar:** fall back to `High - Low`.
- **Constant flat bar with no gap:** TR = 0 (legitimate; downstream ATR handles it).
- **Missing prior close (gaps in data / new session):** decide whether to treat session open as a gap or reset.

## 7. Pitfalls
- Forgetting the previous-close terms reduces TR to the intrabar range and silently understates volatility across gaps.

## 8. References & libraries
- TA-Lib `TRANGE`; pandas-ta `true_range`; tulip `tr`; finta `TR`.
