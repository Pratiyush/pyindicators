# pyindicators — indicator catalog

_Auto-generated from the registry metadata (do not edit by hand)._ **102 indicators** across 9 categories.

## base (7)

| id | outputs | inputs | aliases |
|----|---------|--------|---------|
| `ema` | ema | close | EWMA, Exponentially Weighted MA |
| `rma` | rma | close | SMMA, Wilder's Smoothing, Modified MA, Running MA |
| `sma` | sma | close | Moving Average, MA, Arithmetic MA |
| `stdev` | stdev | close | STDDEV, Standard Deviation, Moving StdDev |
| `true_range` | true_range | high, low, close | TR, TRANGE |
| `variance` | variance | close | VAR, Moving Variance |
| `wma` | wma | close | Linearly Weighted MA, LWMA |

## trend (29)

| id | outputs | inputs | aliases |
|----|---------|--------|---------|
| `adx` | adx, plus_di, minus_di | high, low, close | Average Directional Index, DMI |
| `adxr` | adxr | high, low, close | Average Directional Index Rating |
| `alma` | alma | close | Arnaud Legoux MA |
| `apo` | apo | close | Absolute Price Oscillator |
| `aroon` | aroon_down, aroon_up, aroon_osc | high, low | Aroon, Aroon Oscillator |
| `chop` | chop | high, low, close | Choppiness Index |
| `dema` | dema | close | Double Exponential MA |
| `dx` | dx | high, low, close | Directional Movement Index |
| `fwma` | fwma | close | Fibonacci Weighted MA |
| `hma` | hma | close | Hull Moving Average |
| `kama` | kama | close | Kaufman Adaptive MA |
| `kst` | kst, kst_signal | close | Know Sure Thing, Summed ROC |
| `macd` | macd, macd_signal, macd_hist | close | Moving Average Convergence Divergence |
| `minus_di` | minus_di | high, low, close | -DI, Minus Directional Indicator |
| `plus_di` | plus_di | high, low, close | +DI, Plus Directional Indicator |
| `ppo` | ppo, ppo_signal, ppo_hist | close | Percentage Price Oscillator |
| `pwma` | pwma | close | Pascal Weighted MA |
| `qstick` | qstick | open, close | QStick |
| `sinwma` | sinwma | close | Sine Weighted MA |
| `sma_slope` | sma_slope | close | SMA Slope |
| `supertrend` | supertrend, supertrend_dir | high, low, close | Supertrend |
| `t3` | t3 | close | Tillson T3 |
| `tema` | tema | close | Triple Exponential MA |
| `trima` | trima | close | Triangular MA |
| `trix` | trix, trix_signal | close | Triple Exponential Average |
| `vhf` | vhf | close | Vertical Horizontal Filter |
| `vortex` | vi_plus, vi_minus | high, low, close | Vortex Indicator, VI |
| `vwma` | vwma | close, volume | Volume Weighted MA |
| `zlma` | zlma | close | Zero-Lag EMA, ZLEMA |

## momentum (21)

| id | outputs | inputs | aliases |
|----|---------|--------|---------|
| `ao` | ao | high, low | Awesome Oscillator |
| `bias` | bias | close | Bias |
| `bop` | bop | open, high, low, close | Balance of Power |
| `cci` | cci | high, low, close | Commodity Channel Index |
| `cmo` | cmo | close | Chande Momentum Oscillator |
| `coppock` | coppock | close | Coppock Curve |
| `er` | er | close | Efficiency Ratio, Kaufman Efficiency Ratio |
| `eri` | bull_power, bear_power | high, low, close | Elder Ray, Bull/Bear Power |
| `mom` | mom | close | Momentum |
| `psl` | psl | close | Psychological Line |
| `roc` | roc | close | Rate of Change |
| `rocp` | rocp | close | Rate of Change Percentage |
| `rocr` | rocr | close | Rate of Change Ratio |
| `rocr100` | rocr100 | close | Rate of Change Ratio 100 |
| `rsi` | rsi | close | Relative Strength Index |
| `slope` | slope | close | Slope |
| `stoch` | stoch_k, stoch_d | high, low, close | Stochastic Oscillator, %K/%D |
| `stochrsi` | stochrsi_k, stochrsi_d | close | Stochastic RSI |
| `tsi` | tsi, tsi_signal | close | True Strength Index |
| `uo` | uo | high, low, close | Ultimate Oscillator |
| `willr` | willr | high, low, close | Williams %R, Williams Percent Range |

## volatility (12)

| id | outputs | inputs | aliases |
|----|---------|--------|---------|
| `accbands` | accbands_lower, accbands_mid, accbands_upper | high, low, close | Acceleration Bands, ACCBANDS |
| `atr` | atr | high, low, close | Average True Range |
| `bbands` | bb_middle, bb_upper, bb_lower, bb_bandwidth, bb_pctb | close | Bollinger Bands, BBANDS |
| `chandelier` | chandelier_long, chandelier_short | high, low, close | Chandelier Exit, CE |
| `cvi` | cvi | high, low | Chaikin Volatility |
| `donchian` | dc_lower, dc_middle, dc_upper | high, low | Donchian Channels |
| `hv` | hv | close | Historical Volatility, Realised Volatility |
| `keltner` | kc_lower, kc_middle, kc_upper | high, low, close | Keltner Channels, KC |
| `massi` | massi | high, low | Mass Index |
| `natr` | natr | high, low, close | Normalized ATR |
| `pdist` | pdist | open, high, low, close | Price Distance |
| `ulcer` | ulcer | close | Ulcer Index, UI |

## volume (9)

| id | outputs | inputs | aliases |
|----|---------|--------|---------|
| `ad` | ad | high, low, close, volume | Accumulation/Distribution Line, ADL |
| `adosc` | adosc | high, low, close, volume | Chaikin Oscillator, ADOSC |
| `cmf` | cmf | high, low, close, volume | Chaikin Money Flow |
| `efi` | efi | close, volume | Force Index, Elder Force Index |
| `eom` | eom | high, low, volume | Ease of Movement, EMV |
| `mfi` | mfi | high, low, close, volume | Money Flow Index |
| `obv` | obv | close, volume | On-Balance Volume |
| `pvt` | pvt | close, volume | Price Volume Trend |
| `vwap` | vwap | high, low, close, volume | Volume Weighted Average Price |

## statistics (12)

| id | outputs | inputs | aliases |
|----|---------|--------|---------|
| `entropy` | entropy | close | Shannon Entropy |
| `kurtosis` | kurtosis | close | Rolling Kurtosis |
| `linreg` | linreg | close | Linear Regression, LSMA |
| `linreg_angle` | linreg_angle | close | Linear Regression Angle |
| `linreg_intercept` | linreg_intercept | close | Linear Regression Intercept |
| `linreg_slope` | linreg_slope | close | Linear Regression Slope |
| `mad` | mad | close | Mean Absolute Deviation |
| `median` | median | close | Rolling Median |
| `quantile` | quantile | close | Rolling Quantile |
| `skew` | skew | close | Rolling Skew |
| `tsf` | tsf | close | Time Series Forecast |
| `zscore` | zscore | close | Z-Score |

## relative (1)

| id | outputs | inputs | aliases |
|----|---------|--------|---------|
| `rs_rating` | rs_rating | close | Relative Strength Rating, IBD RS |

## structure (4)

| id | outputs | inputs | aliases |
|----|---------|--------|---------|
| `pct_from_high` | pct_from_high | high, close | Percent From High |
| `pct_from_low` | pct_from_low | low, close | Percent From Low |
| `rolling_high` | rolling_high | high | Highest High, 52-week High |
| `rolling_low` | rolling_low | low | Lowest Low, 52-week Low |

## price_transform (7)

| id | outputs | inputs | aliases |
|----|---------|--------|---------|
| `heikin_ashi` | ha_open, ha_high, ha_low, ha_close | open, high, low, close | Heikin-Ashi, HA |
| `hl2` | hl2 | high, low | MEDPRICE, Median Price |
| `hlc3` | hlc3 | high, low, close | TYPPRICE, Typical Price |
| `midpoint` | midpoint | close | MIDPOINT |
| `midprice` | midprice | high, low | MIDPRICE |
| `ohlc4` | ohlc4 | open, high, low, close | AVGPRICE, Average Price |
| `wcp` | wcp | high, low, close | WCLPRICE, Weighted Close |
