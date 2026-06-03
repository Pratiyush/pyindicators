# Stochastic Oscillator (%K / %D)

- **Category:** momentum oscillator
- **Author:** George Lane (1950s)
- **Default:** %K 14, smoothing 3, %D 3

## 1. What it measures
Where the close sits within the recent high–low range, scaled 0–100.

## 2. How it works
Normalize close against the N-period range to get raw %K; smooth it; %D is an MA of %K.

## 3. Algorithm & formula
```
%K_raw = 100 * (Close - LL(N)) / (HH(N) - LL(N))     # LL/HH = lowest low / highest high
Fast %K = %K_raw ; Fast %D = SMA(%K_raw, d)
Slow %K = SMA(%K_raw, smooth_k) ; Slow %D = SMA(Slow %K, d)
```

## 4. Parameters / best settings
- 14/3/3 (slow, default). Fast 14/3. 5/3/3 for faster signals.

## 5. Outputs & interpretation
- >80 overbought, <20 oversold; %K/%D crossovers; divergence.

## 6. Edge cases
- **HH(N) = LL(N)** (flat window) → %K undefined → set 0, 50, or forward-fill (document).

## 7. Pitfalls
- Confusing fast vs slow (how many smoothings applied).
- SMA vs EMA smoothing differences across libraries.

## 8. References & libraries
- TA-Lib `STOCH`, `STOCHF`; pandas-ta `stoch`; tulip `stoch`; bukosabino/ta `StochasticOscillator`.
