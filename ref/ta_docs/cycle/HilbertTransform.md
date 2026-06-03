# Hilbert Transform Cycle Family (HT_*)

- **Category:** cycle
- **Author:** John Ehlers, *Rocket Science for Traders*
- **Members:** HT_DCPERIOD, HT_DCPHASE, HT_PHASOR, HT_SINE, HT_TRENDMODE, HT_TRENDLINE

## 1. What they measure
The dominant market cycle's period, phase, and whether the market is in "cycle" vs "trend" mode — using digital-signal-processing (Hilbert transform) techniques.

## 2. Shared pipeline (all six)
```
1. 4-bar WMA smooth of price
2. Detrend with Ehlers coefficients (a=0.0962, b=0.5769)
3. Hilbert quadrature -> In-phase (I) and Quadrature (Q) components
4. Phasor advancement with 0.2/0.8 EMA-style smoothing
5. Homodyne discriminator -> dominant cycle period, clamped 6..50 bars
6. Double-smooth (0.33/0.67)
```

## 3. The six outputs
- **HT_DCPERIOD** — dominant cycle length (bars). Lookback **32** (+ unstable). Used to make other indicators adaptive.
- **HT_DCPHASE** — phase 0..360°. Lookback **63** (+ unstable). ~0/360° = cycle low, ~180° = cycle high.
- **HT_PHASOR** — outputs I + Q (diagnostic / building block). Lookback **32** (+ unstable).
- **HT_SINE** — Sine + LeadSine (LeadSine = sin(phase+45°)); crossovers mark cyclic turns; lines stop crossing in trend mode. Lookback **63** (+ unstable).
- **HT_TRENDMODE** — binary 0 (cycle) / 1 (trend). Lookback **63** (+ unstable). Regime selector; pairs with HT_SINE.
- **HT_TRENDLINE** — instantaneous trendline. **This is an Overlap Study (price overlay), NOT a cycle oscillator** — TA-Lib lists it under Overlap Studies, the other five under Cycle Indicators. Lookback **63** (+ unstable). Recommend ≥100 bars warmup.

## 4. Parameters
- Close only, no period parameter. Default unstable period = 0 (so minimum warmup = 32 or 63); raisable up to ~100 via `TA_SetUnstablePeriod`.

## 5. Edge cases
- **Very long, fixed warmup** (32/63 bars) plus optional unstable period — early values are meaningless.
- Recursive EMA-style feedback makes the first ~100 bars unstable even after the nominal lookback.
- Period clamp 6..50 bars; phase wraps at 360°.

## 6. Pitfalls
- Treating HT_TRENDLINE as an oscillator (it's an overlay).
- Under-warming the series; comparing against TA-Lib requires matching the unstable-period setting exactly.
- (Note: PHASOR=32 and DCPHASE=63 lookbacks are inferred from TA-Lib code structure; DCPERIOD=32 and SINE/TRENDMODE/TRENDLINE=63 are verbatim from source.)

## 7. References & libraries
- TA-Lib `HT_DCPERIOD`, `HT_DCPHASE`, `HT_PHASOR`, `HT_SINE`, `HT_TRENDMODE`, `HT_TRENDLINE`. Ehlers' book is the primary source. pandas-ta has `ebsw` (Even Better Sinewave) as a related modern variant.
