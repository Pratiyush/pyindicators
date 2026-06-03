# ADL / CMF / Chaikin Oscillator (Accumulation-Distribution family)

- **Category:** volume
- **Author:** Marc Chaikin

## ADL — Accumulation/Distribution Line
```
MFM = ((Close - Low) - (High - Close)) / (High - Low)   # Money Flow Multiplier, -1..+1
MFV = MFM * Volume
ADL = cumulative sum of MFV
```

## CMF — Chaikin Money Flow
```
CMF = sum(MFV, N) / sum(Volume, N)        # N = 20 or 21
```
Oscillates ~ -0.5..+0.5 in practice.

## Chaikin Oscillator (ADOSC)
```
ADOSC = EMA(ADL, 3) - EMA(ADL, 10)
```

## Parameters / best settings
- CMF N=20/21; ADOSC 3/10.

## Outputs & interpretation
- ADL trend vs price = confirmation/divergence; CMF > 0 accumulation, < 0 distribution; ADOSC = momentum of ADL.

## Edge cases
- **High = Low** → MFM = 0 (NOT NaN) — must special-case.
- **sum(Volume)=0** in CMF window → guard /0.

## Pitfalls
- MFM uses **intrabar** close location, so it ignores close-to-close gaps — a documented disconnect from price action.

## References & libraries
- TA-Lib `AD`, `ADOSC`; pandas-ta `ad`, `cmf`, `adosc`; tulip `ad`, `adosc`; bukosabino/ta `AccDistIndexIndicator`, `ChaikinMoneyFlowIndicator`.
