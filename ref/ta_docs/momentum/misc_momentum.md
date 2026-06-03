# Other Momentum Indicators (ROC, MOM, CMO, AO, BOP, Coppock, RVGI, etc.)

Concise specs; each still gets its own class file.

## ROC / ROCP / ROCR / ROCR100 — Rate of Change
`ROC = 100*(close/close_{t-n} - 1)`; ROCP = fraction; ROCR = ratio; ROCR100 = ratio*100. Edge: `close_{t-n}=0` guard. TA-Lib `ROC`,`ROCP`,`ROCR`,`ROCR100`; tulip `roc`,`rocr`.

## MOM — Momentum
`MOM = close - close_{t-n}`. TA-Lib `MOM`; tulip `mom`.

## CMO — Chande Momentum Oscillator
`CMO = 100*(sumUp - sumDown)/(sumUp + sumDown)` over N. Range ±100. Edge: denom 0 (flat) → 0. TA-Lib `CMO`; tulip `cmo`; pandas-ta `cmo`.

## AO — Awesome Oscillator (Bill Williams)
`AO = SMA(hl2,5) - SMA(hl2,34)`. Zero-line + saucer signals. pandas-ta `ao`; bukosabino/ta `AwesomeOscillatorIndicator`.

## BOP — Balance of Power
`BOP = (Close-Open)/(High-Low)`. Edge: H=L → 0. TA-Lib `BOP`; pandas-ta `bop`.

## APO — Absolute Price Oscillator
`APO = EMA(fast) - EMA(slow)` (MACD line, no signal). TA-Lib `APO`; tulip `apo`.

## Coppock Curve
`WMA( ROC(14) + ROC(11), 10 )`. Long-term bottoming signal. pandas-ta `coppock`; finta `COPP`.

## RVGI — Relative Vigor Index
`RVI = SWMA(Close-Open) / SWMA(High-Low)` with a 4-bar symmetric weighted MA; signal = SWMA(RVI). pandas-ta `rvgi`.

## PVO — Percentage Volume Oscillator
PPO applied to volume: `100*(EMA(vol,12)-EMA(vol,26))/EMA(vol,26)`. pandas-ta `pvo`.

## Elder Ray (Bull/Bear Power)
`BullPower = High - EMA(13)`, `BearPower = Low - EMA(13)`. bukosabino/ta `ElderRayIndex`? finta. 

## SMI Ergodic / KDJ / DeMarker / Laguerre RSI / QQE / RSX / Squeeze
Composite/specialized oscillators — see pandas-ta (`smi`, `kdj`, `squeeze`, `qqe`, `rsx`), freqtrade/technical (Laguerre RSI), and DeMark literature. Document warmup and division guards individually.

**Common edge cases:** `close_{t-n}=0` (ROC family), flat-series denominators (CMO, BOP, RVGI), and double warmup for composites.
