# Other Volume Indicators (Force Index, EOM, NVI/PVI, KVO, PVT, EFI, WAD, VFI)

## Force Index (EFI) — Elder
`EFI = EMA( (Close - Close_{t-1}) * Volume, 13 )`. pandas-ta `efi`; bukosabino/ta `ForceIndexIndicator`.

## Ease of Movement (EOM/EMV) — Arms
`distance = hl2 - hl2_{t-1}; boxratio = (Volume/scale)/(High-Low); EMV = distance/boxratio`, then SMA(14). Edge: H=L guard. pandas-ta `eom`; bukosabino/ta `EaseOfMovementIndicator`.

## Negative / Positive Volume Index (NVI/PVI)
Cumulative index updated only on down-volume (NVI) or up-volume (PVI) days by the day's percent price change. TA-Lib has neither natively; pandas-ta `nvi`,`pvi`; bukosabino/ta.

## Klinger Volume Oscillator (KVO)
See research report; `KVO = EMA(VF,34) - EMA(VF,55)`, signal EMA(13), where VF uses a trend/cumulative-measure term. Edge: cumulative-measure `cm=0` guard; trend carry-forward on equal hlc. pandas-ta `kvo`. (Tulip `kvo` uses a simpler hlc-based VF — document which.)

## Price Volume Trend (PVT)
`PVT = PVT_{t-1} + Volume * (Close - Close_{t-1})/Close_{t-1}`. Edge: `Close_{t-1}=0`. pandas-ta `pvt`.

## Williams Accumulation/Distribution (WAD)
Cumulative based on true range high/low vs prior close. tulip `wad`.

## VFI — Volume Flow Indicator
Cutler's volume-flow oscillator (freqtrade/technical `vfi`). Document its cutoff and smoothing.

## VWMACD / PVOL / PVR / Archer OBV (AOBV)
Volume-weighted MACD and pandas-ta volume utilities — see pandas-ta `vwmacd`(?), `pvol`, `pvr`, `aobv`.

**Common edge cases:** `Close_{t-1}=0` (PVT), `High=Low` (EOM), `sum(volume)=0`, and cumulative-state seeding (NVI/PVI start at 1000 by convention).
