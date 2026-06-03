# Reference Specification for a New Modular Python Technical-Analysis Indicator Library

*A documentation-first blueprint to guide implementation of a pure-Python, one-class-per-indicator TA library. This is the design reference — not the library code.*

## TL;DR
- This reference catalogs **190+ technical indicators across 11 category folders**, mapping each onto a one-class-per-indicator modular design, with formulas, parameters, edge cases, and cross-indicator dependencies drawn from TA-Lib (**158 functions**, including **61 candlestick (CDL) pattern functions**), pandas-ta (the original twopirllc README states "more than 130 Indicators and Utility functions and more than 60 TA Lib Candlestick Patterns"; the maintained pandas-ta-classic fork reports 192 category indicators + 62 CDL patterns = 252 unique), Tulip Indicators (**104**), finta (~80), bukosabino/ta (**43**, the closest existing class-per-indicator analog), QTPyLib, and freqtrade/technical.
- The single most important design decision is to build a **small set of reusable base components** — SMA, EMA, WMA, RMA (Wilder's smoothing), True Range/ATR, and rolling stdev — because the large majority of indicators are compositions of these; getting **Wilder's RMA smoothing and the EMA warmup/seeding exactly right** is the highest-leverage correctness task.
- **Edge-case handling must be standardized library-wide** rather than reimplemented per indicator: division-by-zero on flat/constant series, NaN warmup periods, insufficient lookback, gaps, and the large unstable warmup of the Hilbert Transform family (32–63 fixed bars plus an optional unstable period raisable to ~100).

---

## Key Findings

### Library landscape and coverage
**TA-Lib** is the canonical numerical reference. The official TA-Lib Python tutorial states "There are 158 TA-Lib functions!", and the {talib} R wrapper built on the same C library confirms it "provides 67 technical indicators, 61 candlestick patterns." TA-Lib groups functions into: Overlap Studies, Momentum Indicators, Volume Indicators, Volatility Indicators, Cycle Indicators, Price Transform, Statistic Functions, Math Transform, Math Operators, and Pattern Recognition (candlesticks).

**pandas-ta** uses a similar but expanded taxonomy (candles, cycles, momentum, overlap, performance, statistics, trend, volatility, volume). The original twopirllc README advertises "more than 130 Indicators and Utility functions and more than 60 TA Lib Candlestick Patterns"; the actively maintained fork **pandas-ta-classic** (github.com/xgboosted) reports "252 Unique Indicators & Patterns — 192 category indicators plus 62 CDL patterns via cdl_pattern()." **Tulip Indicators** implements 104 functions in C with a uniform interface (tulipindicators.org: "Tulip Indicators currently implements 104 indicators"). **finta** implements ~80 pure-pandas indicators. **bukosabino/ta** implements 43 indicators in a class-per-indicator style (README: "The library has implemented 43 indicators") — the closest existing analog to the proposed design. **QTPyLib** and **freqtrade/technical** add practical pandas wrappers and a few unique indicators (consensus, vfi, mmar, Laguerre RSI, TradingView-style tv_wma/tv_hma).

### Proposed folder / file structure
```
ta_library/
  __init__.py
  base/
    indicator.py        # Abstract base class: input validation, NaN handling, warmup
    moving_average.py   # MA dispatcher (SMA/EMA/WMA/RMA/...) reused everywhere
    true_range.py       # TR / ATR base reused by many volatility & trend classes
  trend/                # MAs + directional / trend systems (one .md + one class file each)
  momentum/
  volatility/
  volume/
  statistics/
  cycle/
  price_transform/
  candles/
  math_transform/
  utils/
  index.md             # master index (links every indicator file by category)
```
Each category folder gets one Markdown file + one class file per indicator; a top-level `index.md` is the master index. Each indicator class subclasses a common `Indicator` base providing: standardized OHLCV input handling, parameter validation, NaN/warmup conventions, and access to shared base components.

### Cross-indicator dependency graph (recommended build order)
- **Base / foundational (build first):** SMA, EMA, WMA, RMA (Wilder's smoothing / SMMA), rolling stdev & variance, True Range.
- **Second tier (depend on first):** ATR (RMA of TR), DEMA/TEMA/T3 (compositions of EMA), MACD (EMA), Bollinger Bands (SMA + stdev), Keltner (EMA + ATR), Stochastic (rolling min/max), ADX/DMI (RMA of DM and TR), KAMA/VIDYA (adaptive EMA), HMA/ZLEMA (WMA/EMA compositions), Supertrend (ATR), Chandelier Exit (ATR), RSI (RMA of gains/losses).
- **Third tier (composites):** Stochastic RSI (RSI + stochastic), Connors RSI (RSI + streak + percentrank), Schaff Trend Cycle (MACD + stochastic), Chaikin Oscillator (EMA of A/D line), PPO/PVO (EMA), TRIX (triple EMA), KST (ROC + SMA), Coppock (WMA of ROCs).

---

## Details

### Conventions used in every indicator file
1. Name & aliases; 2. Category; 3. What it measures; 4. How it works; 5. Algorithm/formula with initialization; 6. Parameters & defaults/best settings; 7. Outputs & interpretation; 8. Edge cases; 9. Pitfalls; 10. References/libraries.

### Universal edge-case policy (applies library-wide)
- **Division by zero:** Guard every ratio. Constant-price series make ranges (H−L), True Range, summed gains/losses, and stdev zero. RSI: when average loss = 0, RSI = 100 (RS infinite); when average gain = 0, RSI = 0; both zero (flat) → convention (TA-Lib carries forward). Stochastic: when highest_high = lowest_low, %K is undefined → set to 0, 50, or forward-fill. CMF/Money-Flow Multiplier: when H = L, multiplier = 0 (not NaN). Aroon, Williams %R, CCI: same H=L / mean-deviation=0 guards. Fisher Transform: clamp the normalized value strictly inside ±1 or the natural log diverges.
- **Warmup / insufficient lookback:** First N−1 bars of an N-period window are NaN. EMA-family needs a seed — **TA-Lib seeds EMA with an SMA of the first N values** (first valid output at index N−1), whereas pandas `ewm(span=N, adjust=False)` seeds with the first value (valid from index 0). These differ and must be documented per class.
- **NaN handling:** Decide whether to propagate (TA-Lib pushes NaNs to the end in some cases) or skip; standardize. `min_periods` should equal the window unless deliberately relaxed.
- **Gaps / non-continuous sessions:** True Range intentionally captures gaps via prev-close; VWAP must reset per session (use a DatetimeIndex and session boundaries).
- **Unstable period:** Wilder-smoothed indicators (ADX needs ~150 bars for stable values per StockCharts) and Hilbert Transform indicators (32–63-bar fixed lookback plus an optional unstable period raisable to ~100) require long warmup before values are trustworthy.

---

## MASTER INDEX BY CATEGORY

### base/ (reusable components — the backbone, not standalone "indicators")
- **SMA** — Simple Moving Average. `sum(close, N)/N`. Reused by dozens of indicators.
- **EMA** — Exponential Moving Average. `EMA_t = α·P_t + (1−α)·EMA_{t−1}`, α = 2/(N+1). Reused by MACD, PPO, TRIX, TSI, Chaikin, KVO, Keltner, DEMA/TEMA/T3, etc.
- **WMA** — Weighted Moving Average. Linear weights N,N−1,…,1 normalized by N(N+1)/2. Reused by HMA.
- **RMA / Wilder's Smoothing / SMMA** — `RMA_t = (RMA_{t−1}·(N−1) + P_t)/N`, equivalent to EMA with α = 1/N. Reused by RSI, ATR, ADX/DMI, +DM/−DM. Critical to get right.
- **True Range (TR)** — `max(H−L, |H−C_prev|, |L−C_prev|)`. Reused by ATR, Supertrend, Keltner, Chandelier, NATR, Ultimate Oscillator, Vortex.
- **Rolling stdev / variance** — population vs sample distinction matters (TA-Lib uses population). Reused by Bollinger Bands, z-score, RVI.

### trend/ (moving averages + directional / trend systems)
**Moving averages:** SMA, EMA, WMA, DEMA, TEMA, TRIMA, KAMA, HMA, VWMA, ALMA, ZLEMA, T3, FRAMA, VIDYA, SMMA/RMA, FWMA (Fibonacci-weighted), SINWMA (sine-weighted), SWMA (symmetric-weighted), PWMA (Pascal-weighted), HWMA (Holt-Winter), JMA (Jurik), McGinley Dynamic (MCGD), MAMA/FAMA (MESA Adaptive), Rainbow MA, Ehlers Super Smoother (SSF), VAMA (volume-adjusted), EVWMA (elastic volume-weighted), LSMA/linreg MA, Gann HiLo Activator (hilo), TSF (time series forecast).
**Trend / directional systems:** MACD, MACD-Ext, MACD-Fix, PPO, ADX, ADXR, DX, +DI/−DI (PLUS_DI/MINUS_DI), +DM/−DM, Aroon, Aroon Oscillator, Parabolic SAR, SAR-Ext, Supertrend, Ichimoku, Vortex (VI+/VI−), TRIX, KST (Know Sure Thing), DPO (Detrended Price Oscillator), Choppiness Index (CHOP), Vertical Horizontal Filter (VHF), Chande Kroll Stop (CKSP), Q Stick, Schaff Trend Cycle (STC), TTM Trend, Increasing/Decreasing, Pmax, Amat (Archer MA trends), Pivot Points / Central Pivot Range (CPR).

### momentum/ (oscillators)
RSI, Stochastic (%K/%D), Stochastic Fast, Stochastic RSI, Williams %R, CCI, ROC, ROCP, ROCR, ROCR100, Momentum (MOM), TSI (True Strength Index), Ultimate Oscillator (UO), Awesome Oscillator (AO), CMO (Chande Momentum Oscillator), Fisher Transform, Connors RSI, RVGI (Relative Vigor Index), Coppock Curve, BOP (Balance of Power), APO (Absolute Price Oscillator), PPO/PVO, KDJ, SMI Ergodic, Elder Ray Index (Bull/Bear power), Inertia, Bias, BRAR, Center of Gravity (CG), Chande Forecast Oscillator (CFO), Forecast Oscillator (FOSC), Pretty Good Oscillator (PGO), Psychological Line (PSL), QQE (Quantitative Qualitative Estimation), RSX (Relative Strength Xtra), Correlation Trend Indicator (CTI), Squeeze / Squeeze Pro, Williams Alligator, Gator Oscillator, Laguerre RSI, DeMarker, Derivative Oscillator, Relative Strength Levy (RSL), TD Sequential.

### volatility/
Bollinger Bands (+ %B, Bandwidth), ATR, NATR (Normalized ATR), True Range, Keltner Channels, Donchian Channels, Standard Deviation, Chaikin Volatility (CVI), Ulcer Index, Historical Volatility (annualized), Mass Index, Relative Volatility Index (RVI), Acceleration Bands (ACCBANDS), Aberration, Chandelier Exit (CE), Holt-Winter Channel (HWC), Price Distance (PDIST), Elder's Thermometer, APZ (Adaptive Price Zone), Starc Bands.

### volume/
OBV (On-Balance Volume), Accumulation/Distribution Line (AD/ADL), Chaikin Money Flow (CMF), Chaikin Oscillator (ADOSC), Money Flow Index (MFI), VWAP, Volume Profile (VP), Force Index (EFI), Ease of Movement (EOM/EMV), Negative Volume Index (NVI), Positive Volume Index (PVI), Klinger Volume Oscillator (KVO), Volume Weighted MACD (VWMACD), Price Volume Trend (PVT), Volume Oscillator (VOSC/PVO), VFI (Volume Flow Indicator), Market Facilitation Index (MARKETFI), Price-Volume (PVOL), Price Volume Rank (PVR), Williams Accumulation/Distribution (WAD), Archer OBV (AOBV), Elder Force Index.

### statistics/
Linear Regression (linreg), Linear Regression Slope, Linear Regression Intercept, Linear Regression Angle, Time Series Forecast (TSF), Pearson Correlation (CORREL), Beta, Z-Score, Standard Deviation, Variance, Mean Absolute Deviation (MAD), Median, Quantile, Skew, Kurtosis, Entropy, Standard Error (STDERR), R-squared, Covariance.

### cycle/ (Hilbert Transform family + others)
HT_DCPERIOD, HT_DCPHASE, HT_PHASOR, HT_SINE, HT_TRENDMODE, HT_TRENDLINE (overlap, not an oscillator), Even Better Sinewave (EBSW), Detrended Synthetic Price (DSP), MESA Sine Wave (MSW).

### price_transform/
AVGPRICE ((O+H+L+C)/4), MEDPRICE ((H+L)/2, hl2), TYPPRICE ((H+L+C)/3, typical price, hlc3), WCLPRICE (weighted close (H+L+2C)/4, wcp), OHLC4, Heikin-Ashi (HA).

### candles/ (TA-Lib pattern recognition — 61 CDL functions)
61 candlestick pattern functions in the TA-Lib C library, confirmed by the {talib} R wrapper: "{talib} recognizes 61 candlestick patterns—from single-candle formations like Doji and Hammer to multi-candle patterns like Morning Star and Three White Soldiers. Each pattern returns a normalized score: 1 (bullish), -1 (bearish), or 0 (no pattern)." Patterns include Doji, Hammer, Hanging Man, Engulfing, Harami, Morning/Evening Star, Three White Soldiers, Three Black Crows, Shooting Star, Marubozu, Dark Cloud Cover, Piercing, Abandoned Baby, etc. Some functions take a `penetration` parameter.

### math_transform/ & utils/
Vector math (ACOS, ASIN, ATAN, COS, SIN, TAN, EXP, LN, LOG10, SQRT, CEIL, FLOOR), MIN/MAX/SUM/MINMAX over window, crossover/crossany/cross helpers, lag, decay/edecay.

---

## DETAILED PER-INDICATOR SPECIFICATIONS (representative deep dives)

### EMA — Exponential Moving Average
- **Category:** trend/overlap. **Aliases:** EWMA.
- **Measures:** Weighted average giving exponentially more weight to recent prices; faster trend response than SMA.
- **Algorithm:** α = 2/(N+1). Seed: TA-Lib uses SMA of first N values as the first EMA; thereafter `EMA_t = α·P_t + (1−α)·EMA_{t−1}`. (pandas `ewm(span=N, adjust=False)` seeds with the first value — a known discrepancy.)
- **Parameters:** length N (defaults 9, 12, 20, 26, 50, 200 common).
- **Outputs:** single line; interpret via price/EMA crossovers and slope.
- **Edge cases:** Needs warmup; first valid value at index N−1 (TA-Lib) or 0 (pandas seed). Document which seeding you choose.
- **Pitfalls:** Inconsistent seeding causes values to differ between libraries; always reuse one EMA implementation.

### KAMA — Kaufman's Adaptive Moving Average
- **Category:** trend. **Author:** Perry Kaufman. **Default settings KAMA(10,2,30).**
- **Measures:** A moving average that speeds up in trends and slows in noise via an Efficiency Ratio.
- **Algorithm:**
  - Efficiency Ratio ER = |Close − Close_{n ago}| / Σ|Close_i − Close_{i−1}| over n (n=10).
  - Smoothing Constant SC = [ER·(fastest − slowest) + slowest]², where fastest = 2/(2+1), slowest = 2/(30+1).
  - KAMA_t = KAMA_{t−1} + SC·(Price − KAMA_{t−1}).
- **Edge cases:** ER denominator zero on constant price → set SC to slowest²; seed KAMA with first price or SMA.
- **Pitfalls:** SC is squared — forgetting the square is a common bug.

### Supertrend
- **Category:** trend/overlap (uses ATR). **Author:** Olivier Seban (2009). **Defaults:** ATR period 10, multiplier 3 (tighter 7/2 for scalping, wider 14/4 for swing).
- **Algorithm:** HL2 = (H+L)/2. Basic Upper = HL2 + mult·ATR; Basic Lower = HL2 − mult·ATR. Final bands use the carry-forward rule: Final Upper = Basic Upper if (Basic Upper < prev Final Upper) or (prev Close > prev Final Upper) else prev Final Upper (symmetric for lower). Supertrend flips between final upper/lower based on close crossing the active band.
- **Outputs:** trend line + direction (+1/−1); buy when price closes above line (line flips below), sell when below.
- **Edge cases:** Requires ATR warmup; first bars undefined. Stateful carry-forward must be iterative.
- **Pitfalls:** Implementations differ in band carry-forward and flip logic; document precisely. Whipsaws in ranging markets. ATR may use Wilder's RMA or EMA — pick and document.

### Parabolic SAR
- **Category:** trend. **Author:** J. Welles Wilder (New Concepts in Technical Trading Systems, 1978). **Defaults:** AF start 0.02, step 0.02, max 0.20.
- **Algorithm:** SAR_{next} = SAR + AF·(EP − SAR). EP = extreme point (highest high in uptrend / lowest low in downtrend). AF increments by step each time a new EP is made, capped at max. On trend flip, SAR resets to prior EP, AF resets to 0.02, EP resets to current extreme. SAR is clamped so it never penetrates the prior two periods' price range.
- **Edge cases:** Needs initial trend assumption and seed SAR/EP; first value conventionally set from the first two bars.
- **Pitfalls:** The clamping rule (SAR cannot lie inside today's/yesterday's range) is frequently omitted. Whipsaws when sideways.

### ADX / DMI (+DI, −DI, ADX, ADXR, DX)
- **Category:** trend. **Author:** Wilder. **Default:** period 14.
- **Algorithm:**
  - +DM = (High − High_prev) if (High − High_prev) > (Low_prev − Low) and > 0 else 0; −DM symmetric with lows. If both positive, keep the larger; inside bars → both 0.
  - TR as usual. Wilder-smooth +DM, −DM, TR over 14 (first = sum of first 14; then Smoothed_t = Smoothed_{t−1} − Smoothed_{t−1}/14 + Current).
  - +DI = 100·(Smoothed+DM / Smoothed TR); −DI = 100·(Smoothed−DM / Smoothed TR).
  - DX = 100·|+DI − −DI| / (+DI + −DI). ADX = Wilder-smoothed (RMA) of DX. ADXR = (ADX + ADX_{14 ago})/2.
- **Interpretation:** ADX > 25 strong trend, < 20 weak/no trend (Wilder); +DI/−DI crossovers = directional signals.
- **Edge cases:** Needs ~150 bars for stable ADX due to double smoothing (StockCharts). Division by zero when +DI+−DI = 0 → DX = 0.
- **Pitfalls:** First-value seeding (sum vs average) and the two-stage smoothing are the main sources of mismatch.

### Ichimoku Kinko Hyo
- **Category:** trend/overlap. **Author:** Goichi Hosoda. **Defaults:** 9, 26, 52, displacement 26.
- **Algorithm:** Tenkan-sen = (9-period high + 9-period low)/2; Kijun-sen = (26-period high + low)/2; Senkou Span A = (Tenkan + Kijun)/2 shifted +26; Senkou Span B = (52-period high + low)/2 shifted +26; Chikou Span = close shifted −26. Cloud (Kumo) = area between Span A and B.
- **Edge cases:** Forward-shifted spans create future-dated NaNs; Chikou shifted back. **Lookahead/data-leak warning** — Senkou spans and Chikou must be aligned carefully to avoid using future data in backtests (pandas-ta explicitly flags ichimoku for potential data leaks).
- **Pitfalls:** Off-by-one in displacement; "including current period" vs not.

### RSI — Relative Strength Index
- **Category:** momentum. **Author:** Wilder. **Default:** 14.
- **Algorithm:** Gains/losses per bar. Avg Gain/Loss via Wilder's RMA (first = simple average of first 14; then smoothed). RS = AvgGain/AvgLoss. RSI = 100 − 100/(1+RS).
- **Interpretation:** >70 overbought, <30 oversold; divergences; centerline 50.
- **Edge cases:** AvgLoss = 0 → RSI = 100; AvgGain = 0 → RSI = 0; both 0 (flat) → convention (TA-Lib carries forward).
- **Pitfalls:** Using SMA instead of Wilder's RMA gives "Cutler's RSI" — different values. Best settings vary: 2-period RSI for mean-reversion (Connors), 14 standard.

### Connors RSI (CRSI)
- **Category:** momentum. **Author:** Larry Connors. **Defaults:** CRSI(3,2,100).
- **Algorithm:** CRSI = [RSI(Close,3) + RSI(Streak,2) + PercentRank(ROC(1), 100)]/3. Streak = consecutive up/down close count (+n up, −n down, 0 if unchanged). PercentRank = % of prior look-back 1-day returns less than today's.
- **Interpretation:** >90 overbought, <10 oversold (some use 95/5).
- **Edge cases:** Streak reset to 0 on unchanged close; percentrank needs full 100-bar window.
- **Pitfalls:** Applying RSI to the streak series (not price) for the 2nd component is the key subtlety.

### Ultimate Oscillator (UO)
- **Category:** momentum. **Author:** Larry Williams (1976). **Defaults:** 7, 14, 28.
- **Algorithm:** BP (buying pressure) = Close − min(Low, prev Close). TR = max(High, prev Close) − min(Low, prev Close). Avg_n = Σ BP_n / Σ TR_n. UO = 100·(4·Avg7 + 2·Avg14 + Avg28)/(4+2+1).
- **Interpretation:** >70 overbought, <30 oversold; primary signal is divergence.
- **Edge cases:** TR zero only if flat with no gap → guard.

### TSI — True Strength Index
- **Category:** momentum. **Author:** William Blau. **Defaults:** long 25, short 13, signal 7.
- **Algorithm:** PC = Close − prev Close. Double-smooth: PCS = EMA25(PC), PCDS = EMA13(PCS). Same for |PC| → APCDS. TSI = 100·PCDS/APCDS. Signal = EMA7(TSI).
- **Interpretation:** centerline 0; signal-line crossovers; divergences; ±25 cutoffs common.

### Fisher Transform
- **Category:** momentum. **Author:** John Ehlers. **Default:** period 9 (10 also common).
- **Algorithm:** MidPrice = (H+L)/2. Normalize value X to [−1, 1] over n-period high/low range, then clamp to ±0.999. Fisher = 0.5·ln((1+X)/(1−X)), usually with EMA smoothing of the normalized value; trigger line = prior Fisher.
- **Interpretation:** Sharp peaks mark reversals; crossovers of Fisher/trigger; ±1.5/±2 extremes.
- **Edge cases:** Must clamp X strictly inside ±1 or ln diverges (division by zero / infinity). H=L over window → X = 0.

### Bollinger Bands
- **Category:** volatility. **Author:** John Bollinger. **Defaults:** length 20, stdev mult 2.
- **Algorithm:** Middle = SMA(20). Upper/Lower = Middle ± 2·stdev(20) (population stdev). %B = (Close − Lower)/(Upper − Lower). Bandwidth = (Upper − Lower)/Middle.
- **Edge cases:** stdev = 0 on flat series → bands collapse to middle; %B division by zero → guard. Population vs sample stdev mismatch with other libraries.

### Keltner Channels
- **Category:** volatility (EMA + ATR). **Defaults:** EMA 20, ATR 10, mult 2.
- **Algorithm:** Middle = EMA(typical or close). Upper/Lower = Middle ± mult·ATR. (Original Chester Keltner version uses SMA of typical price and a range-based band; modern version uses EMA + ATR — support both via a flag, as bukosabino/ta does with `original_version`.)

### Donchian Channels
- **Category:** volatility. **Default:** 20.
- **Algorithm:** Upper = highest high over N; Lower = lowest low over N; Middle = (Upper+Lower)/2.
- **Pitfalls:** Decide whether the current bar is included (the Turtle system excluded the current bar).

### Ulcer Index
- **Category:** volatility. **Author:** Peter Martin. **Default:** 14.
- **Algorithm:** Percent drawdown R = 100·(Close − MaxClose_N)/MaxClose_N. UI = sqrt(mean(R²) over N).
- **Interpretation:** Downside-volatility/risk measure; higher = more painful drawdowns.

### ATR / NATR / True Range
- **Category:** volatility. **Author:** Wilder. **Default:** 14.
- **Algorithm:** TR = max(H−L, |H−C_prev|, |L−C_prev|). ATR = Wilder RMA of TR (first = simple mean of first 14). NATR = 100·ATR/Close.
- **Edge cases:** First TR (no prev close) = H−L. Reused as a base component everywhere.

### OBV — On-Balance Volume
- **Category:** volume. **Author:** Joe Granville.
- **Algorithm:** OBV_t = OBV_{t−1} + (Volume if Close>Close_prev; −Volume if Close<Close_prev; 0 if equal). Cumulative.
- **Edge cases:** Seed OBV_0 = 0 or first volume; unchanged close adds 0.

### Accumulation/Distribution Line (ADL), Chaikin Money Flow (CMF), Chaikin Oscillator
- **ADL:** Money Flow Multiplier MFM = ((Close−Low)−(High−Close))/(High−Low); Money Flow Volume = MFM·Volume; ADL = cumulative sum.
- **CMF (Marc Chaikin):** Σ(MFV, N) / Σ(Volume, N), N=20 or 21. Oscillates roughly −0.5..+0.5 in practice (theoretical −1..+1).
- **Chaikin Oscillator (ADOSC):** EMA3(ADL) − EMA10(ADL).
- **Edge cases:** H=L → MFM = 0 (not NaN). CMF doesn't account for gaps (uses intrabar close location, not close-to-close) — a documented disconnect from price.

### Money Flow Index (MFI)
- **Category:** volume. **Default:** 14.
- **Algorithm:** Typical Price TP = (H+L+C)/3. Raw Money Flow = TP·Volume. Positive/Negative MF based on TP vs prev TP. Money Ratio = Σ Positive MF / Σ Negative MF over N. MFI = 100 − 100/(1+Money Ratio).
- **Edge cases:** Negative MF sum = 0 → MFI = 100. Unchanged TP excluded.

### Klinger Volume Oscillator (KVO)
- **Category:** volume. **Author:** Stephen Klinger. **Defaults:** fast 34, slow 55, signal 13.
- **Algorithm:** Trend = +1 if (H+L+C) > prev (H+L+C) else −1. dm = H−L. cm = cm_prev + dm if trend unchanged, else dm_prev + dm. Volume Force VF = Volume·|2·(dm/cm − 1)|·Trend·100. KVO = EMA34(VF) − EMA55(VF). Signal = EMA13(KVO).
- **Edge cases:** cm zero → division guard; trend carry-forward on equal (H+L+C). (Tulip's `kvo` uses a simpler hlc-based VF; document which variant you implement.)

### VWAP — Volume Weighted Average Price
- **Category:** volume/overlap. **Algorithm:** cumulative Σ(TypicalPrice·Volume)/Σ(Volume), reset each session.
- **Edge cases:** REQUIRES a DatetimeIndex and session reset; without reset it drifts. freqtrade disabled plain `vwap()` as implicitly forward-looking and recommends `rolling_vwap()` — avoid lookahead.

### Hilbert Transform Cycle Family (TA-Lib, John Ehlers, "Rocket Science for Traders")
All six run a shared pipeline: 4-bar WMA smooth → detrend (Ehlers coefficients a=0.0962, b=0.5769) → Hilbert quadrature/in-phase (Q/I) decomposition → phasor advancement (0.2/0.8 EMA-style smoothing) → homodyne discriminator → dominant cycle period clamped 6–50 bars, then double-smoothed (0.33/0.67). All are flagged "unstable period" in TA-Lib docs.
- **HT_DCPERIOD** (Dominant Cycle Period): outputs dominant cycle length in bars. Close only, no params. **Lookback 32 bars** (+unstable; verbatim from `ta_HT_DCPERIOD.c`). Used to make other indicators adaptive.
- **HT_DCPHASE** (Dominant Cycle Phase): outputs phase 0–360°. **Lookback 63** (+unstable). ~0/360° = cycle low, ~180° = cycle high.
- **HT_PHASOR**: outputs InPhase + Quadrature components (diagnostic/building block). **Lookback 32** (+unstable).
- **HT_SINE**: outputs Sine + LeadSine (LeadSine = sin(phase+45°)); crossovers mark cyclic turns; the two lines stop crossing in trend mode (avoids whipsaw). **Lookback 63** (+unstable).
- **HT_TRENDMODE**: binary 0 (cycle) / 1 (trend). **Lookback 63** (+unstable). Selects trend-following vs mean-reversion regime; pairs with HT_SINE.
- **HT_TRENDLINE** (Instantaneous Trendline): an **Overlap Study** (price overlay, NOT a cycle oscillator — confirmed: TA-Lib lists it under Overlap Studies, the other five under Cycle Indicators). Averages price over one dominant-cycle period to remove the cycle, then 4-3-2-1 weighted smooths. **Lookback 63** (+unstable). Recommend ≥100 bars warmup for convergence.
Default unstable period = 0 (so out-of-the-box minimum warmup = 32 or 63 bars), raisable up to ~100 via `TA_SetUnstablePeriod`; the recursive EMA-style feedback is why early values are unstable. (Note: HT_PHASOR=32 and HT_DCPHASE=63 are inferred from TA-Lib code structure; the other four lookbacks are verbatim from source.)

### Linear Regression family (statistics)
- **linreg:** least-squares fit over N, output endpoint value. **slope, intercept, angle (degrees), TSF (forecast = endpoint + slope), R² (correl²).** Reused by LSMA, Forecast Oscillator, CFO, CTI.

### Heikin-Ashi (price_transform / candles)
- HA_Close = (O+H+L+C)/4; HA_Open = (prev HA_Open + prev HA_Close)/2; HA_High = max(H, HA_Open, HA_Close); HA_Low = min(L, HA_Open, HA_Close). Seed HA_Open with (O+C)/2 of the first bar.

### Awesome Oscillator (AO)
- AO = SMA5(median price) − SMA34(median price), median = (H+L)/2. Zero-line and saucer signals (Bill Williams).

### Coppock Curve
- WMA10 of (ROC14 + ROC11) of close. Long-term momentum / bottoming signal.

### Vortex Indicator (VI+ / VI−)
- VM+ = |High − Low_prev|; VM− = |Low − High_prev|. VI+ = ΣVM+_N / ΣTR_N; VI− = ΣVM−_N / ΣTR_N. Crossovers signal trend changes. Default N=14.

### Chande Momentum Oscillator (CMO)
- CMO = 100·(ΣUp − ΣDown)/(ΣUp + ΣDown) over N (default 20; 14 also used). Range −100..+100.

### Stochastic Oscillator & Stochastic RSI
- %K = 100·(Close − LowestLow_N)/(HighestHigh_N − LowestLow_N); %D = SMA3(%K). Fast vs slow (extra %K smoothing). StochRSI = (RSI − min(RSI_N))/(max(RSI_N) − min(RSI_N)).
- **Edge cases:** HighestHigh = LowestLow → %K undefined → guard (0/50/forward-fill).

---

## Recommendations

**Stage 1 — Build and rigorously test the base layer first.** Implement SMA, EMA (decide and document seeding: TA-Lib SMA-seed vs pandas first-value), WMA, RMA/Wilder, rolling stdev (population), and True Range as standalone reusable classes. Validate against TA-Lib outputs to <1e-6 on a reference dataset. **Benchmark/threshold:** every downstream indicator that uses these should match TA-Lib within floating tolerance; if it doesn't, the bug is almost always in seeding or Wilder smoothing.

**Stage 2 — Implement the high-dependency second tier:** ATR, MACD, Bollinger, Stochastic, RSI, ADX/DMI, DEMA/TEMA/T3, KAMA, HMA, Supertrend. These cover the majority of real-world usage and exercise the base components.

**Stage 3 — Composite / third tier:** Stochastic RSI, Connors RSI, Schaff Trend Cycle, Chaikin Oscillator, TSI, KST, Ichimoku (with an explicit lookahead flag), Hilbert Transform family (with documented long warmup).

**Stage 4 — Breadth:** remaining oscillators, volume, statistics, candlestick patterns, math transforms.

**Design rules:**
- One abstract `Indicator` base class enforcing input schema (OHLCV), parameter validation, and a uniform NaN/warmup policy.
- A single `MovingAverage` dispatcher so any indicator can swap its MA type (TA-Lib MA-type pattern: 0=SMA, 1=EMA, 2=WMA, 3=DEMA, 4=TEMA, 5=TRIMA, 6=KAMA, 7=MAMA, 8=T3).
- Never reimplement EMA/ATR/RMA inside another indicator — always compose from base.
- Add a `talib_compatible` flag where seeding/smoothing conventions differ.
- Ship a test suite comparing against TA-Lib and pandas-ta where overlap exists; document expected divergences (EMA seeding, population vs sample stdev, Wilder vs SMA in RSI).

**Thresholds that change the plan:** If exact TA-Lib parity is a hard requirement, mirror TA-Lib's seeding and unstable-period semantics exactly and add a compatibility test gate. If the priority is pandas-native ergonomics, prefer `ewm`/`rolling` and document the (small) numerical differences instead.

## Caveats
- **Indicator counts differ by library and version.** Authoritative figures: TA-Lib = 158 functions (61 of them CDL candlestick patterns); the original twopirllc pandas-ta README states "more than 130 Indicators ... and more than 60 TA Lib Candlestick Patterns," while the pandas-ta-classic fork reports 252 unique (192 indicators + 62 CDL); Tulip Indicators = 104; bukosabino/ta = 43. Treat marketing counts ("150+", "200") as approximate.
- **Many indicators have competing formula conventions** (Keltner original vs modern; Stochastic smoothing; CMO period; RSI Wilder vs Cutler; Donchian current-bar inclusion; KVO Klinger vs Tulip variant). The library should pick a documented default and expose flags.
- **Some "indicators" in source libraries are utilities/math operators** (add, sub, crossover, lag) rather than analytical indicators; group them in utils/math_transform.
- **Hilbert Transform PHASOR (32) and DCPHASE (63) lookback numbers are inferred** from TA-Lib code structure; DCPERIOD (32) and SINE/TRENDMODE/TRENDLINE (63) are verbatim from source.
- **Candlestick pattern recognition (61 TA-Lib CDL functions)** involves many heuristic body/shadow thresholds and a `penetration` parameter for some; each needs its own careful spec — treat the candles/ folder as a sub-project. Each CDL function returns a normalized score: 1 (bullish), −1 (bearish), or 0 (no pattern).
- This reference is documentation to guide implementation; **all formulas should be re-validated against a numerical reference (TA-Lib) during coding**, since some were captured from secondary educational sources rather than primary source code.