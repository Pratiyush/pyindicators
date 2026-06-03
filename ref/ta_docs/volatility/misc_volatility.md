# Other Volatility Indicators (StdDev, Chaikin Vol, Mass Index, RVI, Chandelier, HV, ACCBANDS)

## Standard Deviation — see base/RollingStdev.md. TA-Lib `STDDEV`.

## Chaikin Volatility (CVI)
`100 * (EMA(High-Low,N) - EMA(High-Low,N)_{t-roc}) / EMA(High-Low,N)_{t-roc}`. Rate of change of an EMA of the range. 

## Mass Index (Dorsey)
`sum( EMA(H-L,9) / EMA(EMA(H-L,9),9), 25 )`. "Reversal bulge" > 27 then < 26.5. pandas-ta `massi`.

## Relative Volatility Index (RVI)
RSI computed on rolling **stdev** instead of price. pandas-ta `rvi`.

## Chandelier Exit (CE)
`LongStop = HH(N) - mult*ATR`, `ShortStop = LL(N) + mult*ATR` (N=22, mult=3). ATR-based trailing stop. pandas-ta `chandelier`? freqtrade.

## Historical Volatility (HV)
`stdev(ln(close/close_{t-1}), N) * sqrt(annualization)` (252 for daily). Annualized realized vol.

## ACCBANDS — Acceleration Bands (Headley)
`Upper = High*(1 + 4*(High-Low)/(High+Low))`, `Lower = Low*(1 - 4*(High-Low)/(High+Low))`, each SMA'd. TA-Lib `ACCBANDS`.

## NATR — see ATR_NATR.md.

**Common edge cases:** flat-range → EMA(H-L)=0 division guards (CVI, Mass Index), `close=0` for HV log returns, ATR warmup for Chandelier.
