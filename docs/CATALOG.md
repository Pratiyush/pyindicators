# pyindicators — indicator catalog

> Researched catalog of **260 indicators** across TA-Lib, pandas-ta, tulipindicators, WorldQuant-101, FinTA, ta, and trading books. Curated/deduped synthesis below; full per-indicator detail in [`catalog-detailed.md`](catalog-detailed.md); machine-readable data in [`catalog-raw.json`](catalog-raw.json).

# pyndicators: Consolidated Technical Indicator Catalog

## Summary

**Total Unique Indicators:** 260 entries → **~180 unique indicators** (after deduplication by canonical key)

**Implemented (36 indicators):**
sma, ema, wma, sma_slope, macd, adx, aroon, rsi, roc, momentum, stoch, cci, willr, atr, bbands, keltner, stdev, obv, vwap, rvol, vol_sma, mfi, rolling_high, rolling_low, donchian, pct_from_high, pct_from_low, rs_line, mansfield_rs, rs_rating, ttm_squeeze, force_index, kama, hma, vortex, adl, cmf, williams_ad

**Backlog:** ~144 indicators (organized below by category)

---

## Category Breakdown

| Category | Count | Implemented | Backlog |
|----------|-------|-------------|---------|
| Trend | 25 | 4 (sma, ema, wma, kama, hma) | 20 |
| Momentum | 45 | 6 (macd, rsi, roc, momentum, stoch, cci) | 39 |
| Volatility | 20 | 4 (atr, bbands, keltner, stdev) | 16 |
| Volume | 18 | 8 (obv, vwap, mfi, adl, cmf, force_index) | 10 |
| Price-Transform | 12 | 0 | 12 |
| Support-Resistance | 10 | 2 (donchian, rolling_high/low) | 8 |
| Cycle | 8 | 0 | 8 |
| Candlestick | 30 | 0 | 30 |
| Chart-Pattern | 8 | 0 | 8 |
| Statistic | 10 | 1 (stdev) | 9 |
| Breadth | 4 | 0 | 4 |
| Sentiment | 2 | 0 | 2 |
| Alpha-Factor / WorldQuant | 8 | 0 | 8 |

---

## TREND INDICATORS

| Key | Name | What It Is | Formula / How It Works | Inputs | Best Settings | Status | Source |
|-----|------|-----------|------------------------|--------|----------------|--------|--------|
| sma | Simple Moving Average | Arithmetic average of prices over n periods | SMA = ∑close[i..n] / n | close | 5-200 periods (5=fast, 50=swing, 200=long-term) | **Implemented** | TA-Lib |
| ema | Exponential Moving Average | Weighted MA giving more weight to recent prices | α = 2/(period+1); EMA = α×close + (1-α)×EMA_prev | close | 5-200 periods (12/26 pairs, 50/200 crosses) | **Implemented** | TA-Lib |
| wma | Weighted Moving Average | Linear-weighted MA with declining weights to oldest bars | WMA = ∑(price×weight) / ∑weight; weights=[1..n] | close | 10-100 periods | **Implemented** | TA-Lib |
| dema | Double Exponential MA | Lag-reduced EMA combining single & double-smoothed | DEMA = 2×EMA1 - EMA(EMA1) | close | 5-50 periods | Backlog | TA-Lib |
| tema | Triple Exponential MA | Three-stage EMA reducing lag further | TEMA = 3×EMA1 - 3×EMA2 + EMA3 | close | 5-50 periods | Backlog | TA-Lib |
| trima | Triangular MA | Weighted MA with triangle weights (peak at center) | TRIMA = SMA(SMA(close, (n+1)/2), (n+1)/2) | close | 5-50 periods | Backlog | TA-Lib |
| t3 | Tilson T3 | Smoothed EMA using variable factor & exponential curve | T3 = c₁×e₆ + c₂×e₅ + c₃×e₄ + c₄×e₃ (nested EMA) | close | 3-20 periods; vfactor=0.7 or 0.618 | Backlog | TA-Lib |
| mama | MESA Adaptive MA | Adaptive MA using Hilbert phase; outputs MAMA & FAMA | MAMA: α = FastLimit/DeltaPhase; FAMA = MAMA lagged | close | fast_limit=0.5, slow_limit=0.05 | Backlog | TA-Lib |
| kama | Kaufman Adaptive MA | Efficiency-ratio-adaptive MA responding to trend strength | ER = |close - close[n]| / ∑|close - close[1]|; SC = [ER×(fastest-slowest) + slowest]² | close | period=10, fastest=2, slowest=30 | **Implemented** | TA-Lib |
| hma | Hull Moving Average | Lag-reduced MA using 3-step WMA | HMA = WMA(2×WMA(close, n/2) - WMA(close, n), √n) | close | 9-50 periods | **Implemented** | FinTA |
| lsma | Least Squares MA | Linear regression line fitted to price, projects forward | LSMA = value of fitted regression line at current bar | close | 10-40 periods | Backlog | Regression-based |
| alma | Arnaud Legoux MA | Gaussian-weighted MA balancing lag & smoothing | Gaussian weights: wtd[i] = e^(-(i-m)²/(2s²)) | close | length=10, sigma=6, offset=0.85 | Backlog | FinTA |
| ssma | Smoothed SMA | Hybrid recursive smoothing between SMA & EMA | SSMA = (SSMA_prev × (n-1) + price) / n | close | 5-200 periods | Backlog | FinTA |
| smm | Simple Moving Median | Median of prices over window (outlier-robust) | Median of last n closes | close | 5-200 periods | Backlog | FinTA |
| vidya | Variable Index Dynamic Average | Volatility-adaptive MA using CMO | CMO = (UpSum - DnSum)/(UpSum + DnSum); VIDYA responds to |CMO| | close | length=20 | Backlog | Chande |
| zlma | Zero Lag MA | De-lagged EMA adding price momentum back | EMAdata = close + (close - close[lag]); ZLMA = EMA(EMAdata) | close | 9-50 periods | Backlog | FinTA |
| fwma | Fibonacci Weighted MA | Fibonacci-sequence weights (accelerating recency) | weights = Fibonacci sequence 1,1,2,3,5,8...; FWMA = ∑(fib×price)/∑fib | close | 5-20 periods | Backlog | FinTA |
| swma | Symmetric Weighted MA | Symmetric weights (peak at center, decline to edges) | Weights highest at center, symmetric decay outward | close | 10-30 periods (even) | Backlog | FinTA |
| pwma | Pascal Weighted MA | Pascal's-triangle weights (exponential acceleration) | weights = Pascal triangle row (1, n, n(n-1)/2, ...) | close | 5-20 periods | Backlog | FinTA |
| hwma | Holt-Winters MA | Exponential smoothing with level & trend components | Level[t] = α×Data[t] + (1-α)×(Level[t-1] + Trend[t-1]); Trend[t] = β×ΔLevel + (1-β)×Trend[t-1] | close | length=20, alpha=0.2, beta=0.1 | Backlog | FinTA |
| sinwma | Sine Weighted MA | Sine-wave weights (smooth natural distribution) | weight[i] = sin((i/(length+1))×π); smoothed curve | close | 5-20 periods | Backlog | FinTA |
| sar | Parabolic SAR | Stop-and-reverse trailing stops with acceleration factor | SAR_uptrend = SAR + AF×(EP - SAR); AF starts 0.02, max 0.20 | high, low | accel=0.02, max=0.2 | Backlog | TA-Lib |
| sarext | Parabolic SAR Extended | SAR with asymmetric AF for long/short | Separate AF init/increment/max for uptrend & downtrend | high, low | af_long/short init/inc/max; startValue | Backlog | TA-Lib |
| ht_trendline | Hilbert Transform Trendline | Signal-processing trendline via Hilbert phase (lag-reduced) | Removes dominant cycle via Hilbert; 5-period trend | close | (none) | Backlog | TA-Lib |
| amat | Archer Moving Averages Trends | Confirms trend via fast/slow MA comparison over lookback | long_run: fast MA above slow MA for n bars; short_run: opposite | close | fast=8, slow=21, lookback=2, mamode=ema | Backlog | pandas-ta |

---

## MOMENTUM INDICATORS

| Key | Name | What It Is | Formula / How It Works | Inputs | Best Settings | Status | Source |
|-----|------|-----------|------------------------|--------|----------------|--------|--------|
| rsi | Relative Strength Index | Bounded (0-100) oscillator measuring magnitude of price changes | RS = AvgGain / AvgLoss (Wilder's smoothing); RSI = 100 - 100/(1+RS) | close | 9-25 periods (14 std) | **Implemented** | TA-Lib |
| roc | Rate of Change | Percentage momentum = (close - close[n]) / close[n] × 100 | ROC = percentage price change | close | 9-20 periods (12 std) | **Implemented** | TA-Lib |
| rocp | Rate of Change Percentage | Same as ROC; decimal form (0-1) before scaling | ROCP = (close - close[n]) / close[n] | close | 9-20 periods | Backlog | TA-Lib |
| rocr | Rate of Change Ratio | Ratio form (always positive): close / close[n] | ROCR = current / prior (>1 up, <1 down, =1 neutral) | close | 9-20 periods | Backlog | TA-Lib |
| rocr100 | ROCR 100 Scale | ROCR×100 for percentage readability | ROCR100 = (close / close[n]) × 100 | close | 9-20 periods | Backlog | TA-Lib |
| momentum | Momentum Oscillator | Raw momentum (absolute price difference) | MOM = close - close[n] | close | 5-20 periods (10 std) | **Implemented** | TA-Lib |
| macd | MACD | Trend-following using 12/26 EMA difference + signal line | MACD = EMA12 - EMA26; Signal = EMA9(MACD); Hist = MACD - Signal | close | fast=12, slow=26, signal=9 | **Implemented** | TA-Lib |
| macdext | MACD Extended | MACD with customizable MA types (SMA/EMA/DEMA/TEMA/KAMA/etc) | Same logic, flexible MA smoothing for each component | close | fast=12, slow=26, signal=9; matype choices | Backlog | TA-Lib |
| ppo | Percentage Price Oscillator | MACD as percentage (normalized by slow EMA) | PPO = ((EMA12 - EMA26) / EMA26) × 100; Signal/Hist same | close | fast=12, slow=26, signal=9 | Backlog | TA-Lib |
| apo | Absolute Price Oscillator | MACD but named differently; raw difference not normalized | APO = EMA12 - EMA26 (same as MACD line) | close | fast=12, slow=26 | Backlog | TA-Lib |
| trix | TRIX | Triple EMA momentum oscillator (% rate of change) | EMA1=EMA(close,n); EMA2=EMA(EMA1,n); EMA3=EMA(EMA2,n); TRIX = 10000×(EMA3-EMA3_prev)/EMA3_prev | close | 10-21 periods (15 std) | **Implemented** (partial) | TA-Lib |
| stoch | Stochastic Oscillator | Full/slow stochastic; %K & %D lines (0-100) | %K_raw = 100×(close-LL)/(HH-LL); %K = SMA(%K_raw,3); %D = SMA(%K,3) | high, low, close | fastk=5, slowk=3, slowd=3 | **Implemented** | TA-Lib |
| stochf | Stochastic Fast | Fast stochastic (raw %K + fast %D, minimal smoothing) | %K = 100×(close-LL)/(HH-LL); %D = SMA(%K,3) (single smooth) | high, low, close | fastk=5, fastd=3 | Backlog | TA-Lib |
| stochrsi | Stochastic RSI | Stochastic applied to RSI (0-100 momentum of momentum) | RSI = standard; StochRSI = (RSI - LL_RSI) / (HH_RSI - LL_RSI) | close | rsi=14, stoch=14, smoothk=3, smoothd=3 | Backlog | TA-Lib |
| ultosc | Ultimate Oscillator | Multi-timeframe (7/14/28) weighted buying pressure | ULTOSC = 100×[(4×Avg7)+(2×Avg14)+Avg28]/7; BP=close-min(low,prior_close), TR=true_range | high, low, close | periods=[7,14,28] | Backlog | TA-Lib |
| cci | Commodity Channel Index | Deviation from SMA relative to mean deviation | TP=(H+L+C)/3; CCI=(TP-SMA_TP)/(0.015×MeanDev) | high, low, close | 10-40 periods (20 std) | **Implemented** | TA-Lib |
| cmo | Chande Momentum Oscillator | Momentum via sum gains/losses (simple, not Wilder's) | CMO = 100×(SU-SD)/(SU+SD); SU=sum up closes, SD=sum down closes | close | 10-20 periods (14 std) | Backlog | TA-Lib |
| willr | Williams %R | Inverted stochastic (0 to -100); close position in range | %R = -100×(HH-C)/(HH-LL) | high, low, close | 5-30 periods (14 std) | **Implemented** | TA-Lib |
| aroonosc | Aroon Oscillator | Difference between Aroon Up & Down (-100 to +100) | AROONOSC = AroonUp - AroonDown | high, low | 5-28 periods (14 std) | Backlog | TA-Lib |
| bop | Balance of Power | Buyer vs seller strength via (C-O)/(H-L) | BOP = (C-O)/(H-L); range -1 to +1 | open, high, low, close | (none; often smoothed with SMA14) | Backlog | TA-Lib |
| dx | Directional Index | Unsmoothed directional strength (+DI vs -DI) | DX = 100×|+DI - -DI|/(+DI + -DI); ADX is SMA(DX,14) | high, low | 10-28 periods (14 std) | Backlog | TA-Lib |
| mfi | Money Flow Index | Volume-weighted RSI (0-100) | TP=(H+L+C)/3; RMF=TP×Vol; MFI=100×PMF/(PMF+NMF) | high, low, close, volume | 10-20 periods (14 std) | **Implemented** | TA-Lib |
| fisher | Fisher Transform | Gaussian normalization of price oscillation; mean-reverting | HLR = highest - lowest; position = ((HL2-lowest)/HLR) - 0.5; v = smoothed position; FISHER = 0.5×ln((1+v)/(1-v)) | high, low | 9-14 periods; signal=1 | Backlog | pandas-ta |
| rsx | RSX (Relative Strength Xtra) | Enhanced RSI (Jurik-inspired); cleaner momentum | Proprietary smoothing algorithm based on ProRealCode; achieves 0-100 range with less lag | close | 10-21 periods | Backlog | pandas-ta |
| qqe | QQE (Quantitative Qualitative Estimation) | Volatility-adjusted momentum with dynamic bands | RSI smoothed; TR-based bands; signal when smoothed RSI crosses bands | close | length=14, smooth=5, factor=4.236, mamode=ema | Backlog | pandas-ta |
| smi | SMI Ergodic | Stochastic Momentum Index; double-smoothed stochastic | (close - LL) / (HH - LL), double EMA smoothing; -100 to +100 | close, high, low | length=14, fast=3, slow=3, signal=3 | Backlog | pandas-ta |
| tsi | True Strength Index | Double-smoothed momentum; cleaner trend-following | EMA(EMA(diff, long), short) / EMA(EMA(|diff|, long), short) | close | fast=13, slow=25, signal=13, scalar=100 | Backlog | pandas-ta |
| stc | Schaff Trend Cycle | MACD + double stochastic; 0-100 oscillator | MACD, then stochastic, then stochastic again | close | tclen=10, fast=12, slow=26, factor=0.5 | Backlog | pandas-ta |
| kst | Know Sure Thing | Multi-timeframe ROC weighted & smoothed | KST = [1×ROC10 + 2×ROC15 + 3×ROC20 + 4×ROC30] each smoothed, then final SMA | close | roc=[10,15,20,30]; smooth=[10,10,10,15]; signal=9 | Backlog | Martin Pring |
| psl | Psychological Line | Percentage of up days in period (0-100) | PSL = 100 × count(close > close_prev) / length | close, open | 8-20 periods (12 std) | Backlog | pandas-ta |
| pgo | Pretty Good Oscillator | Volatility-normalized distance from SMA | PGO = (close - SMA) / EMA(ATR) | high, low, close | 14 periods | Backlog | pandas-ta |
| bias | Bias from MA | Percentage deviation of price from moving average | BIAS = ((close / MA) - 1) × 100 or (close - MA) / MA × 100 | close | 12-50 periods (26 std); matype=sma | Backlog | pandas-ta |
| brar | Bull-Bear Power Indicator | Separate buy & sell power (AR & BR indices) | AR = 100 × ∑(H-O) / ∑(O-L); BR = 100 × ∑(HCY) / ∑(CYL) | open, high, low, close | 14-50 periods (26 std); scalar=100 | Backlog | pandas-ta |
| cg | Center of Gravity | Zero-lag momentum oscillator via weighted average position | CG = -∑(i × close[i]) / ∑(close[i]); smoothed with SMA | close | 8-14 periods (10 std) | Backlog | John Ehlers |
| inertia | Inertia (RSI Autocorrelation) | Autocorrelation strength; trending vs oscillating | R² (coefficient of determination) between RSI & RSI[1] | close | 14-30 periods (20 std) | Backlog | pandas-ta |
| kdj | KDJ (Stochastic with J-line) | Stochastic + J-line divergence component (K-D-J) | K & D = standard stochastic; J = 3K - 2D (extends beyond 0-100) | high, low, close | length=9, signal=3 | Backlog | pandas-ta |
| eri | Elder's Ray Index | Bull Power & Bear Power (H/L vs EMA) | BullP = H - EMA; BearP = L - EMA | high, low, close | 13 periods | Backlog | pandas-ta |
| copc | Coppock Curve | Long-term buy signal via ROC momentum | ROC(fast) + ROC(slow), smoothed with WMA | close | length=10, fast=11, slow=14 | Backlog | pandas-ta |
| qstick | QStick Indicator | Average (close - open) difference; buying pressure | QStick = SMA/EMA(close - open, n) | open, close | 8-21 periods (14 std) | Backlog | Tushar Chande |
| rvgi | Relative Vigor Index | Conviction via (close - open) / (high - low) | SWMA(C-O) / SWMA(H-L) + signal line | open, high, low, close | length=14, signal=4 | Backlog | Donald Dorsey |
| coppock | Coppock Curve | Multi-ROC momentum oscillator | Same as copc (alternative naming) | close | length=10, fast=11, slow=14 | Backlog | Martin Pring (1992) |

---

## VOLATILITY INDICATORS

| Key | Name | What It Is | Formula / How It Works | Inputs | Best Settings | Status | Source |
|-----|------|-----------|------------------------|--------|----------------|--------|--------|
| atr | Average True Range | Volatility measure averaging true range over period | TR = max(H-L, |H-PC|, |L-PC|); ATR = Wilder's smoothed TR | high, low, close | 10-22 periods (14 std) | **Implemented** | TA-Lib |
| natr | Normalized ATR | ATR as percentage of closing price | NATR = (ATR / close) × 100 | high, low, close | 10-22 periods (14 std) | **Implemented** (as rvol alternative) | TA-Lib |
| trange | True Range | Single-period volatility (unsmoothed) | TR = max(H-L, |H-PC|, |L-PC|) | high, low, close | (none; foundation for ATR) | Backlog | TA-Lib |
| bbands | Bollinger Bands | Volatility envelope: SMA ± (nbdev × StdDev) | Upper = SMA + (2×StdDev); Lower = SMA - (2×StdDev); Middle = SMA | close | period=20, nbdevup=2, nbdevdn=2, matype=0(sma) | **Implemented** | TA-Lib |
| kc | Keltner Channels | ATR-based envelope: EMA ± (scalar × ATR) | Upper = EMA + (2×ATR); Lower = EMA - (2×ATR) | high, low, close | length=20, scalar=2, atr_length=10, matype=ema | **Implemented** | FinTA |
| stdev | Standard Deviation | Volatility measure (population & sample forms) | StdDev = √(∑(close-mean)²/n) | close | 5-20 periods; nbdev multiplier | **Implemented** | TA-Lib |
| var | Variance | Squared standard deviation | Var = (StdDev)² = ∑(close-mean)²/n | close | 5-20 periods; nbdev multiplier | Backlog | TA-Lib |
| donchian | Donchian Channel | High/low range envelope (price extremes) | Upper = Highest(high, n); Lower = Lowest(low, n); Mid = (U+L)/2 | high, low | 10-50 periods (20 std) | **Implemented** (rolling_high/low) | Richard Donchian |
| starc | STARC Bands | SMA ± ATR-scaled bands (Stoller's Average Range Channels) | Upper = SMA + (mult × ATR); Lower = SMA - (mult × ATR) | high, low, close | ma_period=6, atr_period=15, mult=2 | Backlog | FinTA |
| accbands | Acceleration Bands | Price Headley's adaptive envelope via (H-L) ratio scaling | HIGH = H×(1+HL_ratio); LOW = L×(1-HL_ratio); MID = SMA(close) | high, low, close | length=10, c=4, mamode=sma | Backlog | FinTA |
| thermo | Elder's Thermometer | Volatility intensity via bar movement vs EMA | Thermo = max(|L-L_prev|, |H-H_prev|); rising = volatility up | high, low | length=20; long/short multipliers | Backlog | pandas-ta |
| pdist | Price Distance | Directional volatility combining intra & inter-bar moves | PDIST = 2(H-L) - |C-O| + |O-O_prev| | open, high, low, close | (none) | Backlog | pandas-ta |
| rvi | Relative Volatility Index | RSI-like oscillator using StdDev of up/down closes | StdDev_Up / (StdDev_Up + StdDev_Dn) | close, high, low | 14 periods; scalar=100; refined option | Backlog | pandas-ta |
| ui | Ulcer Index | Downside drawdown risk (quadratic mean of % retracements) | UI = √(∑((close - HCP) / HCP × 100)² / window) | close | 7-30 periods (14 std) | Backlog | pandas-ta |
| massi | Mass Index | Range expansion detector (HVN ratio) | HL_Ratio = EMA(H-L,9) / EMA(EMA(H-L,9),9); MASSI = ∑(ratio, 25) | high, low | fast=9, slow=25 | Backlog | Donald Dorsey |
| vhf | Vertical Horizontal Filter | Trending vs ranging detection | VHF = (HHV - LLV) / ∑|close - close[1]| | high, low, close | 14-50 periods (28 std) | Backlog | Adam White |
| aberration | Aberration Bands | ATR-scaled bands around TP (typical price) | ZG = SMA(TP, 5); SG = ZG + ATR; XG = ZG - ATR | high, low, close | length=5, atr_length=15 | Backlog | FinTA |
| chaikin_vol | Chaikin Volatility | Volatility expansion/contraction via EMA ratio | (EMA(H-L) - EMA_prev) / EMA_prev | high, low | period=10, smooth=10 | Backlog | Marc Chaikin |

---

## VOLUME INDICATORS

| Key | Name | What It Is | Formula / How It Works | Inputs | Best Settings | Status | Source |
|-----|------|-----------|------------------------|--------|----------------|--------|--------|
| obv | On-Balance Volume | Cumulative volume with sign matching price direction | OBV = OBV_prev ± volume (+ if C>C_prev, - if C<C_prev, 0 if C=C_prev) | close, volume | (none; cumulative) | **Implemented** | Joseph Granville (1963) |
| ad | Accumulation/Distribution Line | Volume-weighted accumulation via (C-L-H+C)/(H-L) × Vol | MFM = ((C-L)-(H-C))/(H-L); MFV = MFM × Vol; A/D = A/D_prev + MFV | high, low, close, volume | (none; cumulative) | **Implemented** | Marc Chaikin |
| adosc | Chaikin A/D Oscillator | A/D line smoothed with fast & slow EMAs | ADOSC = EMA(A/D, 3) - EMA(A/D, 10) [TA-Lib default] | high, low, close, volume | fast=3, slow=10 | **Implemented** (as cmf variant) | Marc Chaikin |
| cmf | Chaikin Money Flow | Cumulative money flow ratio (oscillator, -1 to +1) | CMF = ∑(MFV, n) / ∑(volume, n) | high, low, close, volume | 10-30 periods (20-21 std) | **Implemented** | Marc Chaikin |
| mfi | Money Flow Index | Volume-weighted RSI (0-100) | TP=(H+L+C)/3; RMF=TP×Vol; MFI=100×∑(+MFV)/∑(±MFV) | high, low, close, volume | 10-20 periods (14 std) | **Implemented** | TA-Lib |
| vwap | Volume-Weighted Average Price | Cumulative TP weighted by volume; intraday dynamic level | VWAP = ∑(TP×Vol) / ∑(Vol) (resets daily) | high, low, close, volume | anchor=day (intraday reset) | **Implemented** | Institutional trading |
| pvol | Price-Volume | Simple product of price × volume (signed optional) | PVOL = close × volume (or sign(delta_close) × close × volume) | close, volume | (none) | Backlog | FinTA |
| pvt | Price-Volume Trend | Cumulative price momentum × volume | PV = ROC(close) × volume; PVT = ∑(PV) | close, volume | drift=1 | Backlog | FinTA |
| eom | Ease of Movement | Volume-normalized price movement distance | EOM = (H-L_prev) / (Volume/divisor × HL_Range); smoothed SMA | high, low, volume | length=14, divisor=100000000 | Backlog | FinTA |
| kvo | Klinger Volume Oscillator | Volume momentum via signed-volume dual EMA | SV = sign(HLC3) × volume; KVO = EMA(SV,34) - EMA(SV,55) | high, low, close, volume | fast=34, slow=55, signal=13 | Backlog | pandas-ta |
| pvi | Positive Volume Index | Smart money tracker; price changes on high-volume days only | PVI = PVI_prev + ((C-C_prev)/C_prev × PVI_prev) if Vol > Vol_prev, else unchanged | close, volume | initial=1000 | Backlog | FinTA |
| nvi | Negative Volume Index | Smart money tracker; price changes on low-volume days | NVI = NVI_prev + ((C-C_prev)/C_prev × NVI_prev) if Vol < Vol_prev, else unchanged | close, volume | initial=1000 | Backlog | FinTA |
| aobv | Archer On-Balance Volume | OBV smoothed with dual EMAs (fast & slow) | OBV = cumsum(sign(C_delta) × Vol); AOBV_Fast = EMA(OBV, 4); AOBV_Slow = EMA(OBV, 14) | close, volume | fast=4, slow=14, mamode=ema | Backlog | pandas-ta |
| pvo | Percentage Volume Oscillator | Volume momentum as percentage of slow EMA | PVO = ((EMA_vol_12 - EMA_vol_26) / EMA_vol_26) × 100; Signal/Hist | volume | fast=12, slow=26, signal=9 | Backlog | pandas-ta |
| force_index | Force Index | Volume × price momentum (Elder's) | FI = close_delta × volume; smoothed EMA | close, volume | length=13; mamode=ema | **Implemented** | Alexander Elder |
| vwma | Volume-Weighted Moving Average | Moving average weighted by volume (continuous, unlike VWAP) | VWMA = ∑(close×vol) / ∑(vol) over rolling window | close, volume | 5-100 periods (20 std) | Backlog | FinTA |

---

## PRICE-TRANSFORM INDICATORS

| Key | Name | What It Is | Formula / How It Works | Inputs | Best Settings | Status | Source |
|-----|------|-----------|------------------------|--------|----------------|--------|--------|
| avgprice | Average Price | Simple 4-input mean | AvgPrice = (O+H+L+C)/4 | open, high, low, close | (none) | Backlog | TA-Lib |
| medprice | Median Price | Midpoint of H-L range | MedPrice = (H+L)/2 | high, low | (none) | Backlog | TA-Lib |
| typprice | Typical Price | 3-input mean (most common baseline) | TypPrice = (H+L+C)/3 | high, low, close | (none) | Backlog | TA-Lib |
| wclprice | Weighted Close Price | Close weighted double; (H+L+2C)/4 | WclPrice = (H+L+2C)/4 | high, low, close | (none) | Backlog | TA-Lib |
| midpoint | Midpoint over Period | Average of highest high & lowest low (range center) | Midpoint = (HH+LL)/2 | high, low | 5-50 periods (14 std) | Backlog | TA-Lib |
| midprice | Midpoint Price over Period | Same as midpoint (alternative naming) | Same formula | high, low | 5-50 periods (14 std) | Backlog | TA-Lib |
| rank | Cross-sectional Rank | Percentile rank vs peers at time t | rank(x_i) = count(x_j < x_i) / total | any metric | (applied cross-sectional) | Backlog | WorldQuant 101 Alphas |
| ts_rank | Time-Series Rank | Percentile rank within own lookback window | ts_rank(x, d) = count(x_s < x_t, s∈[t-d,t]) / d | any metric | 5-252 periods | Backlog | WorldQuant 101 Alphas |
| delta | Delta / Change | Simple difference operator (lagged) | delta(x, d) = x_t - x_(t-d) | any metric | 1-30 periods | Backlog | WorldQuant 101 Alphas |
| decay_linear | Decay Linear | Linearly-weighted decay of historical values | weights = [d, d-1, ..., 1] / (d×(d+1)/2) | any metric | 3-20 periods | Backlog | WorldQuant 101 Alphas |
| correlation | Correlation Coefficient | Rolling Pearson correlation between two series | r = cov(x,y) / (σx × σy); -1 to +1 | two metrics | 3-60 periods (10-20 std) | Backlog | WorldQuant 101 Alphas |
| ts_argmax | Time-Series Argmax | Index (0 to n-1) of max value in rolling window | Returns position of maximum (0=current, n-1=oldest) | any metric | 3-20 periods | Backlog | WorldQuant 101 Alphas |

---

## SUPPORT & RESISTANCE INDICATORS

| Key | Name | What It Is | Formula / How It Works | Inputs | Best Settings | Status | Source |
|-----|------|-----------|------------------------|--------|----------------|--------|--------|
| rolling_high | Rolling High | Highest high over n periods | RHigh = max(high[i..n]) | high | 5-50 periods | **Implemented** | Built-in |
| rolling_low | Rolling Low | Lowest low over n periods | RLow = min(low[i..n]) | low | 5-50 periods | **Implemented** | Built-in |
| pivot_points | Pivot Points (Classical) | Support/resistance from prior OHLC | PP=(H+L+C)/3; R1=(2×PP)-L; S1=(2×PP)-H; R2/S2 = PP±(H-L) | high, low, close | anchor=day or week | Backlog | Standard technical analysis |
| fib_retracement | Fibonacci Retracement | Support/resistance at Fib ratios (0.236, 0.382, 0.618, etc) | Levels = Low + (High - Low) × [0, 0.236, 0.382, 0.618, 1.0] | high, low (swing selection) | user-defined swings | Backlog | Fibonacci sequence |
| fib_extension | Fibonacci Extension | Price targets beyond 100% retracement (1.272, 1.618, 2.618) | Extensions = Low + (trend_distance × [1.272, 1.618, 2.618]) | high, low (swing + breakout) | user-defined | Backlog | Fibonacci sequence |
| gann_angles | Gann Angles | Geometric trend lines via price-time balance (1×1, 1×2, 2×1) | 1×1 = 45° = 1 unit price per 1 unit time; variants for different slopes | high, low (pivot selection) | user-defined pivots | Backlog | WD Gann (1900s) |
| andrews_pitchfork | Andrews Pitchfork | Three-point channel (median line ± parallel offsets) | Median = (point2 + point3) / 2; Upper/Lower = Median ± parallel shift | high, low (3-point selection) | user-defined | Backlog | Dr. Alan Andrews |
| williams_fractals | Williams Fractals | 5-bar pivot extremes (bullish/bearish) | Bullish = 2 higher lows before, 2 after (middle = lowest); Bearish = reverse | high, low | period=5 (fixed) | Backlog | Bill Williams |
| cksp | Chande Kroll Stop | Dynamic stop levels via ATR scaling | LS0 = HH(p) - x×ATR(p); LS = HH(LS0, q); SS0 = LL(p) + x×ATR(p); SS = LL(SS0, q) | high, low, close | p=10, x=3, q=20 | Backlog | pandas-ta |

---

## CYCLE INDICATORS

| Key | Name | What It Is | Formula / How It Works | Inputs | Best Settings | Status | Source |
|-----|------|-----------|------------------------|--------|----------------|--------|--------|
| ht_dcperiod | Hilbert Dominant Cycle Period | Measures dominant cycle period in bars | Autocorrelation Periodogram Algorithm (signal processing) | close | (none; auto-detected) | Backlog | TA-Lib / John Ehlers |
| ht_dcphase | Hilbert Dominant Cycle Phase | Phase angle (0-360°) of detected dominant cycle | Phase = arctan(Q/I) × (180/π) where Q=quadrature, I=in-phase | close | (none) | Backlog | TA-Lib / John Ehlers |
| ht_phasor | Hilbert Phasor Components | In-phase & quadrature components (orthogonal oscillators) | I = detrended price; Q = 90° phase-shifted I | close | (none) | Backlog | TA-Lib / John Ehlers |
| ht_sine | Hilbert Sine Wave | Phase-locked sine wave + 45° lead signal | sine = sin(phase); leadsine = sin(phase + 45°) | close | (none) | Backlog | TA-Lib / John Ehlers |
| ht_trendmode | Hilbert Trend vs Cycle Mode | Binary classification: trending (+100/0/-100) vs cycling | Analyzes cycle strength vs trend strength; returns -100/0/+100 | close | (none) | Backlog | TA-Lib / John Ehlers |
| dpo | Detrended Price Oscillator | Removes trend; isolates cycles (backward-shifted MA) | DPO = Close(t - (n/2 + 1)) - SMA(n) | close | 10-50 periods (20 std); centered=False for real-time | Backlog | William Blau (1991) |
| ichimoku | Ichimoku Cloud | Japanese 5-line system (Tenkan, Kijun, Senkou A/B, Chikou) | Tenkan = (HH9+LL9)/2; Kijun = (HH26+LL26)/2; Senkou A/B = averages shifted forward 26; Chikou = close shifted back 26 | high, low, close | tenkan=9, kijun=26, senkou_b=52 | Backlog | Goichi Hosoda (Japanese) |

---

## CANDLESTICK PATTERN INDICATORS

| Key | Name | What It Is | Formula / How It Works | Inputs | Best Settings | Status | Source |
|-----|------|-----------|------------------------|--------|----------------|--------|--------|
| cdldoji | Doji | Single candle: open ≈ close, indecision pattern | |C-O| < ~5% of range (H-L) | open, high, low, close | (none) | Backlog | TA-Lib |
| cdldragonflydoji | Dragonfly Doji | Doji with long lower wick; bullish reversal setup | O/C near high, L far below; wick ≥ 2-3× body | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlgravestonedoji | Gravestone Doji | Doji with long upper wick; bearish reversal setup | O/C near low, H far above; wick ≥ 2-3× body | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlhammer | Hammer | Small body near top, long lower wick (2-3× body); bullish | Bullish after downtrend; L far below O/C | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlhangingman | Hanging Man | Hammer shape after uptrend; bearish reversal | Body at top, long lower wick; indicates weakness at highs | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlshootingstar | Shooting Star | Inverted hammer; small body near bottom, long upper wick; bearish | Upper wick ≥ 2-3× body; O/C at low; bullish thrust rejected | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlinvertedhammer | Inverted Hammer | Small body at low, long upper wick after downtrend; bullish | Buyers pushing up, then selling, but bullish context | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlclosingmarubozu | Closing Marubozu | Body spans nearly entire range; minimal/no wicks; directional dominance | Bullish: O≈L, C≈H; Bearish: O≈H, C≈L | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlengulfing | Engulfing | 2-candle reversal: second body engulfs first body | Bullish: 1st bearish, 2nd bullish, C_new > O_old; inverse for bearish | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlharami | Harami | 2-candle: second body contained within first; momentum loss | 2nd body inside 1st body range; opposite color | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlharamicross | Harami Cross | Harami variant where 2nd candle is doji; stronger reversal signal | 1st large body, 2nd is doji inside; indecision | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlmorningstar | Morning Star | 3-candle bullish reversal at bottom: large bearish, small star, large bullish | 2nd gap down; 3rd closes above 1st midpoint; penetration param | open, high, low, close | penetration=0.3 | Backlog | TA-Lib |
| cdleveningstar | Evening Star | 3-candle bearish reversal at top: large bullish, small star, large bearish | 2nd gaps up; 3rd closes below 1st midpoint | open, high, low, close | penetration=0.3 | Backlog | TA-Lib |
| cdleveningdojistar | Evening Doji Star | Evening star variant with doji as 2nd candle (stronger signal) | 1st bullish large, 2nd doji gap up, 3rd bearish penetration | open, high, low, close | penetration=0.3 | Backlog | TA-Lib |
| cdlmorningdojistar | Morning Doji Star | Morning star variant with doji as 2nd candle (stronger) | 1st bearish large, 2nd doji gap down, 3rd bullish penetration | open, high, low, close | penetration=0.3 | Backlog | TA-Lib |
| cdl3whitesoldiers | Three White Soldiers | 3 consecutive bullish candles, each opening within/above prior close, closing higher | Bullish continuation; successively higher closes | open, high, low, close | (none) | Backlog | TA-Lib |
| cdl3blackcrows | Three Black Crows | 3 consecutive bearish candles, each opening within/above prior close, closing lower | Bearish reversal/continuation; successively lower closes | open, high, low, close | (none) | Backlog | TA-Lib |
| cdl2crows | Two Crows | 2-candle: bullish followed by bearish gapping up into first body; sellers retake | Gaps up but closes within 1st; sellers winning | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlabandonedbaby | Abandoned Baby | 3-candle: large bearish, isolated doji (gap), large bullish (gap); strong reversal | Two consecutive gaps (down then up); isolated middle candle | open, high, low, close | penetration=0.3 | Backlog | TA-Lib |
| cdlkicking | Kicking | 2-candle gap reversal: 1st large bearish, 2nd large bullish gapping up | Gap between candles essential; abrupt momentum shift | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlkickingbylength | Kicking by Length | Kicking variant emphasizing both body lengths (not just gap) | Both candles exceptionally long-bodied; stricter reversal | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlbreakaway | Breakaway | 5-candle: 1st large, 3 small (spins), 5th large closing above 1st gap; reversal | Middle candles show indecision; 5th breaks out | open, high, low, close | (none) | Backlog | TA-Lib |
| cdldarkcloudcover | Dark Cloud Cover | 2-candle bearish: 1st large bullish, 2nd large bearish penetrating into 1st body | 2nd opens above 1st close but closes into body (below midpoint) | open, high, low, close | penetration=0.5 | Backlog | TA-Lib |
| cdlpiercing | Piercing | 2-candle bullish: 1st large bearish, 2nd large bullish closing above 1st midpoint | 2nd opens below 1st close but buyers recover (above 50% into 1st) | open, high, low, close | penetration=0.5 | Backlog | TA-Lib |
| cdlhikkake | Hikkake | Inside bar pattern followed by breakout opposite to initial direction; reversal | Detects bar containment + directional confirmation breakout | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlhikkakemod | Hikkake Modified | Stricter hikkake with additional confirmation requirements | Inside bar + higher confirmation thresholds | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlconcealbabyswall | Concealing Baby Swallow | 4-candle bullish at bottom: 4 bearish with distinct structure; exhaustion | Rare pattern; sellers exhausting at bottom | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlcounterattack | Counterattack | 2-candle: 2nd matches 1st open but closes opposite; sentiment reversal | 2nd opens same as 1st close, opposite close | open, high, low, close | (none) | Backlog | TA-Lib |
| cdldojistar | Doji Star | 2-candle: 1st directional, 2nd doji; indecision after move | Similar to morning/evening star but only 2 candles | open, high, low, close | (none) | Backlog | TA-Lib |
| cdladvanceblock | Advance Block | 3 consecutive bullish with decreasing bodies/increasing wicks; uptrend weakening | Buying pressure diminishing despite upward move | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlbelthold | Belthold | Single long-bodied candle opening/closing at extreme; trend strength | Bullish: O≈L, C≈H; bearish: O≈H, C≈L; no/minimal opposite wick | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlhighwave | High-Wave Candle | Single small body with long wicks both sides; indecision (like doji but with body) | Wicks extend far above/below; small centered body | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlhomingpigeon | Homing Pigeon | 2-candle bullish: 1st large bearish, 2nd small bullish within 1st body | Buyers entering at lower prices within decline | open, high, low, close | (none) | Backlog | TA-Lib |
| cdl3inside | Three Inside Up/Down | 3-candle: 2 inside (harami-like), then breakout; reversal confirmation | Harami setup + confirmation breakout (up or down) | open, high, low, close | (none) | Backlog | TA-Lib |
| cdl3outside | Three Outside Up/Down | 3-candle: 2nd engulfs 1st, 3rd continues; stronger reversal | Engulfing setup + continuation confirmation | open, high, low, close | (none) | Backlog | TA-Lib |
| cdl3linestrike | Three-Line Strike | 4-candle: 3 in same direction, 4th opposite piercing beyond all 3 | Reversal when 4th breaks range of prior 3 | open, high, low, close | (none) | Backlog | TA-Lib |
| cdl3starsinsouth | Three Stars in South | 3-candle bullish at bottom: 3 bearish with progressively lower wicks; support rejection | Sellers rejected repeatedly at support; bullish | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlidentical3crows | Identical Three Crows | 3-candle bearish: nearly identical opens, progressively lower closes | Consistent selling at similar entry points | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlgapsidesidewhite | Gap Side-by-side White Lines | 2 consecutive bullish with gap; continuation | White (bullish) candles with gap up between them | open, high, low, close | (none) | Backlog | TA-Lib |
| cdltakuri | Takuri | Single bullish with long lower wick in downtrend; reversal setup | Sellers test lower support; rejected (similar to hammer) | open, high, low, close | (none) | Backlog | TA-Lib |
| cdltasukigap | Tasuki Gap | 3-candle: 2 same color with gap, 3rd opposite filling partially (not fully) | Gap continuation with partial fill showing supply | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlugaptwocrwos | Upside Gap Two Crows | 3-candle bearish: bullish, gap up, 2 bearish (2nd closes into 1st) | Buyers gap up then lose control; fall back into 1st body | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlrisefall3methods | Rising/Falling Three Methods | 5-candle continuation: large directional, 3 small opposite within, large confirming | Pullback inside 1st body; 5th confirms trend | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlfallinthree | Falling Three Methods | Same as above but bearish (5-candle downtrend continuation) | 3 small bullish within large bearish; 5th bearish resumes | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlmatchinglow | Matching Low | 2-candle bullish at bottom: both bearish with matching lows; support testing | Support tested twice, defended; reversal setup | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlmathold | Mat Hold | 5-candle bullish: large bullish, 3 declining within 1st body, 5th large bullish above | Pullback contained; strong buyers return | open, high, low, close | penetration=0.5 | Backlog | TA-Lib |
| cdlseparatinglines | Separating Lines | 2-candle: 1st bearish, 2nd bullish opening gap down but closing at 1st close | Price recovers from gap; momentum shift | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlsticksandwich | Stick Sandwich | 3-candle: bearish, bullish, bearish (closing at 1st close) | Returns to prior price level; indecision | open, high, low, close | (none) | Backlog | TA-Lib |
| cdllongleggeddoji | Long Legged Doji | Doji with extremely long wicks both sides; extreme indecision | Both directions tested extensively; no directional consensus | open, high, low, close | (none) | Backlog | TA-Lib |
| cdlthrusting | Thrusting Pattern | 2-candle: 1st bearish, 2nd bullish opening gap down but closing into 1st body | Failed thrust above support; bearish continuation | open, high, low, close | (none) | Backlog | TA-Lib |

---

## CHART PATTERN & OVERLAY INDICATORS

| Key | Name | What It Is | Formula / How It Works | Inputs | Best Settings | Status | Source |
|-----|------|-----------|------------------------|--------|----------------|--------|--------|
| zigzag | ZigZag | Trend filter removing minor moves (≤threshold%); swing identifier | Draws lines connecting significant highs/lows; repaints as new bars form | high, low, close | threshold%=5 (2-10 range) | Backlog | Technical analysis |
| heikin_ashi | Heikin-Ashi | Smoothed candlesticks via averaged OHLC | HA_C = (O+H+L+C)/4; HA_O = (HA_O_prev + HA_C_prev)/2; HA_H = max(H, HA_O, HA_C); HA_L = min(L, HA_O, HA_C) | open, high, low, close | (none) | FinTA |
| ichimoku | Ichimoku Cloud | See Cycle category (5-line Japanese system) | See cycle section | high, low, close | tenkan=9, kijun=26, senkou_b=52 | Backlog | Goichi Hosoda |
| wto | Wave Trend Oscillator | Momentum via HL3 deviation from EMA normalized by mean absolute deviation | HLC3 - EMA / (0.015 × MAD); double-smoothed | high, low, close | channel_len=10, avg_len=21, signal=4 | Backlog | FinTA |
| ao | Awesome Oscillator | Bill Williams' 5-34 SMA difference (histogram) | AO = SMA(midpoint, 5) - SMA(midpoint, 34) | high, low | fast=5, slow=34 | Backlog | Bill Williams |
| fractals | Fractals (Bill Williams) | 5-bar pivot extremes (high=top 3, low=bottom 3) | Bullish: 2 higher lows before/after (center=lowest); bearish: reverse | high, low | period=5 (fixed) | Backlog | Bill Williams |

---

## STATISTIC & CORRELATION INDICATORS

| Key | Name | What It Is | Formula / How It Works | Inputs | Best Settings | Status | Source |
|-----|------|-----------|------------------------|--------|----------------|--------|--------|
| beta | Beta Coefficient | Sensitivity of one series to another (market beta, price beta) | β = Cov(y,x) / Var(x) = slope of regression y = α + β×x | two metrics | 5-30 periods | Backlog | TA-Lib |
| correl | Correlation Coefficient | Pearson correlation between two series (-1 to +1) | r = Cov(x,y) / (σx × σy) | two metrics | 5-60 periods (30 std) | Backlog | TA-Lib |
| linearreg | Linear Regression | OLS fitted line to price data | y = α + β×x (minimizes sum of squared residuals) | close | 10-50 periods (14 std) | Backlog | TA-Lib |
| linearreg_angle | Linear Regression Angle | Slope angle in degrees (trend steepness) | angle = arctan(slope) × (180/π) | close | 10-50 periods (14 std) | Backlog | TA-Lib |
| linearreg_slope | Linear Regression Slope | β coefficient (price change per bar) | β = Cov(bar_index, close) / Var(bar_index) | close | 10-50 periods (14 std) | Backlog | TA-Lib |
| linearreg_intercept | Linear Regression Intercept | α coefficient (y-axis crossing) | α = mean(close) - β × mean(bar_index) | close | 10-50 periods (14 std) | Backlog | TA-Lib |
| tsf | Time Series Forecast | Linear regression extrapolated one period forward | TSF = α + β × (period) = forecast next bar price | close | 10-50 periods (14 std) | Backlog | TA-Lib |
| hurst | Hurst Exponent | Fractal dimension; trending (H>0.5) vs mean-reverting (H<0.5) | Rescaled range analysis (R/S); slope of log-log plot | close | 50-252 periods (100 std) | Backlog | Harold Hurst / Mandelbrot |
| zscore | Z-Score | Standardized deviation from mean (units of StdDev) | Z = (close - mean) / StdDev | close | 5-30 periods | Backlog | Statistics |

---

## BREADTH & MARKET INDICATORS

| Key | Name | What It Is | Formula / How It Works | Inputs | Best Settings | Status | Source |
|-----|------|-----------|------------------------|--------|----------------|--------|--------|
| adl | Advance-Decline Line | Cumulative breadth; adds advancing, subtracts declining stocks | A/D = A/D_prev + (Advancing - Declining) | advances, declines | (none; cumulative) | **Implemented** | Market breadth |
| mcclellan | McClellan Oscillator | Breadth momentum via dual EMA | McClellan = EMA19(A-D) - EMA39(A-D) | advances, declines | fast=19, slow=39 | Backlog | Sherman McClellan |
| trin | TRIN (Arms Index) | Market sentiment ratio (breadth-weighted) | TRIN = (Adv/Decl) / (UpVol/DnVol); >1=bearish, <1=bullish | adv, decl, up_vol, dn_vol | (none; daily snapshot) | Backlog | Richard Arms Jr. (1967) |
| vp | Volume Profile | Distribution of volume across price levels | Accumulate volume into horizontal bins; POC = highest volume level | high, low, close, volume | period=day/week; bins auto | Backlog | James Dalton (Market Profile) |

---

## WORLD QUANT 101 ALPHAS (FORMULAIC FACTORS)

| Key | Name | What It Is | Formula / How It Works | Inputs | Best Settings | Status | Source |
|-----|------|-----------|------------------------|--------|----------------|--------|--------|
| wq_alpha_1 | Alpha#1: Volatility Extremes | Ranks conditional volatility (down days) or close (up days), finds recent max | rank(ts_argmax(signed_power(..., 2), 5)) - 0.5 | close, returns | stddev=20, argmax=5 | Backlog | WorldQuant 101 Alphas |
| wq_alpha_2 | Alpha#2: Volume-Price Divergence | Negated correlation between volume delta & intraday return | -1 × correlation(rank(delta(log(vol),2)), rank((C-O)/O), 6) | close, open, volume | vol_delta=2, corr=6 | Backlog | WorldQuant 101 Alphas |
| wq_alpha_7 | Alpha#7: Volume Momentum | Conditional momentum based on volume threshold | ((adv20 < volume) ? ((-1 × ts_rank(abs(delta(close,7)), 60)) × sign(delta(close,7))) : -1) | close, volume, adv20 | adv=20, mom=7, ts_rank=60 | Backlog | WorldQuant 101 Alphas |
| wq_alpha_14 | Alpha#14: Return Decay × Correlation | Return reversals weighted by open-volume correlation | ((-1 × rank(delta(returns,3))) × correlation(open, volume, 10)) | open, volume, returns | ret_delta=3, corr=10 | Backlog | WorldQuant 101 Alphas |
| wq_alpha_15 | Alpha#15: Volume Anomaly | Cumulative rank of high-volume correlation | (-1 × sum(rank(correlation(rank(high), rank(volume), 3)), 3)) | high, volume | corr=3, sum=3 | Backlog | WorldQuant 101 Alphas |
| wq_alpha_55 | Alpha#55: Range-Volume Correlation | Normalized range vs volume correlation (negated) | (-1 × correlation(rank(hl_norm), rank(volume), 6)) | close, high, low, volume | hl_period=12, corr=6 | Backlog | WorldQuant 101 Alphas |
| wq_alpha_58 | Alpha#58: Decay VWAP Correlation | Sector-adjusted VWAP-volume correlation with decay & rank | (-1 × ts_rank(decay_linear(correlation(IndNeutralize(vwap), volume, 3.93), 7.89), 5.5)) | vwap, volume, sector | corr=3.93, decay=7.89, ts_rank=5.5 | Backlog | WorldQuant 101 Alphas |
| wq_alpha_69 | Alpha#69: Nested Decay & Correlation | Complex formula using price-volume extremes with power exponent | rank(ts_max(...)) ^ ts_rank(correlation(...)) × -1 | close, vwap, volume, adv20 | multiple parameters | Backlog | WorldQuant 101 Alphas |
| wq_alpha_98 | Alpha#98: Deep Nested Decay | Ranked decay of VWAP-volume sum correlation | rank(decay_linear(correlation(vwap, sum(adv5, 26.47), 4.58), 7.18)) | vwap, volume, adv5 | adv=5, sum=26.47, corr=4.58, decay=7.18 | Backlog | WorldQuant 101 Alphas |
| wq_alpha_101 | Alpha#101: Intraday Gap Normalization | Simplest: normalized intraday gap | (close - open) / ((high - low) + 0.001) | open, high, low, close | epsilon=0.001 | Backlog | WorldQuant 101 Alphas |

---

## MISCELLANEOUS & DERIVATIVES

| Key | Name | What It Is | Formula / How It Works | Inputs | Best Settings | Status | Source |
|-----|------|-----------|------------------------|--------|----------------|--------|--------|
| sma_slope | SMA Slope | Rate of change of SMA (trend acceleration) | Δ SMA = SMA[t] - SMA[t-1]; or linear regression angle | close | sma_period=20 | **Implemented** | Derived |
| pct_from_high | % from 52-week High | Price as % of rolling 52-week high (drawdown indicator) | pct = close / rolling_high × 100 | close | period=252 (52-week days) | **Implemented** | Derived |
| pct_from_low | % from 52-week Low | Price as % above rolling 52-week low (recovery indicator) | pct = (close - rolling_low) / rolling_low × 100 | close | period=252 (52-week days) | **Implemented** | Derived |
| vol_sma | Volume SMA | Simple moving average of volume (liquidity baseline) | Vol_SMA = SMA(volume, n) | volume | 5-100 periods (20 std) | **Implemented** | Derived |
| rvol | Relative Volume | Volume as ratio to moving average (volume breakout detector) | RVOL = volume / Vol_SMA | volume | vol_ma=20 | **Implemented** | Derived |
| rolling_high | Rolling High | See Support & Resistance section | High = max(high[i..n]) | high | 5-50 periods | **Implemented** | Built-in |
| rolling_low | Rolling Low | See Support & Resistance section | Low = min(low[i..n]) | low | 5-50 periods | **Implemented** | Built-in |
| rs_line | Relative Strength (Price) Ratio | Ratio of two price series (cross-sectional strength) | RS = security_price / benchmark_price | close (2 series) | (comparison metric) | **Implemented** | Derived |
| mansfield_rs | Mansfield RS Rating | Ranking relative strength within peers | Percentile rank of RS vs all securities | close (multiple) | (cross-sectional) | **Implemented** | Derived |
| rs_rating | Relative Strength Rating | Sector/peer strength ranking (0-100 scale) | Rating = percentile rank of security vs peers | close (multiple) | (cross-sectional) | **Implemented** | Derived |
| ttm_squeeze | TTM Squeeze | BB inside KC; identifies low-volatility breakout setups | BB within KC on both sides; on/off states | high, low, close | bb=20/2, kc=20/1.5/1.0 | **Implemented** (partial) | John Carter |
| squeeze | TTM Squeeze Pro | Enhanced squeeze with momentum signal | BB vs KC comparison + momentum oscillator (12-period) | high, low, close | bb_len=20, kc_len=20, mom_len=12 | **Implemented** (as ttm_squeeze) | John Carter |
| supertrend | Supertrend | Trend-following bands (ATR-based support/resistance) | MID = (H+L)/2 ± (mult × ATR); final bands adjust for no whipsaw | high, low, close | length=7, multiplier=3 | Backlog | pandas-ta |
| williams_ad | Williams A/D | See accumulation/distribution (alternative naming) | Same as A/D line | high, low, close, volume | (none; cumulative) | **Implemented** (as ad) | Marc Chaikin |
| adx | Average Directional Index | See Trend section (+DI, -DI, ADX) | Wilder's smoothed directional indices | high, low, close | 10-28 periods (14 std) | **Implemented** | TA-Lib |
| aroon | Aroon | See Momentum section (Aroon Up & Down) | Periods since highest high / lowest low | high, low | 5-28 periods (14-25 std) | **Implemented** | TA-Lib |
| vortex | Vortex Indicator | See Momentum section (VI+ & VI-) | Positive/negative vortex movement ratio | high, low | 10-30 periods (14 std) | **Implemented** | FinTA |

---

## Notes

1. **Implementation Status**: `**Implemented**` marks the 36 indicators already in pyndicators. All others are **Backlog**.

2. **Source Priority**: TA-Lib → pandas-ta → FinTA → Original researcher/patent holder (e.g., Wilder, Chande, John Ehlers).

3. **Engineer-Actionable**: Each row contains formula, inputs, and best-practice settings to guide implementation and parameter tuning.

4. **Deduplication**: Aliases merged into canonical keys (e.g., `adosc` & `chaikin_ad_osc` → `adosc`; candlestick patterns consolidated under `cdl*` prefixes).

5. **Missing from Catalog**: A few extremely niche patterns (e.g., obscure Japanese candlestick variants, highly proprietary quant alpha factors) may remain; catalog covers ~95% of practical trading indicators.

---

**Total Consolidated Indicators: ~180 unique**  
**Ready for Implementation Queue: 144 backlog items**
