# Other Moving Averages (TRIMA, ZLEMA, T3, ALMA, VWMA, FRAMA, VIDYA, McGinley)

Quick specs for the remaining trend/overlap MAs. Each should still get its own class file.

## TRIMA — Triangular MA
`TRIMA(N) = SMA(SMA(price, ceil((N+1)/2)), floor((N+1)/2)+1?)` — a double-SMA that weights the middle of the window most. TA-Lib `TRIMA`, tulip `trima`.

## ZLEMA — Zero-Lag EMA (Ehlers)
`ZLEMA = EMA(price + (price - price_{t-lag}), N)`, `lag = (N-1)/2`. Subtracts the lag by adding the momentum back. pandas-ta `zlma`, finta `ZLEMA`.

## T3 — Tillson T3
A 6-fold EMA cascade with a volume-factor `v` (default 0.7) producing a smooth low-lag line. `T3 = c1*e6 + c2*e5 + c3*e4 + c4*e3` with coefficients from `v`. TA-Lib `T3`, tulip `t3`, pandas-ta `t3`.

## ALMA — Arnaud Legoux MA
Gaussian-weighted MA over the window with offset (`0.85`) and sigma (`6`) controlling lag vs smoothness. pandas-ta `alma`.

## VWMA — Volume Weighted MA
`VWMA = sum(price*volume, N) / sum(volume, N)`. Edge: `sum(volume)=0` → guard. pandas-ta `vwma`, finta `VW_MA`.

## FRAMA — Fractal Adaptive MA (Ehlers)
EMA whose alpha adapts via the fractal dimension of recent price. pandas-ta `frama` (in some forks).

## VIDYA — Variable Index Dynamic Average (Chande)
EMA whose alpha is scaled by a volatility ratio (CMO-based or stdev-based). pandas-ta `vidya`.

## McGinley Dynamic
`MD_t = MD_{t-1} + (price - MD_{t-1}) / (k*N*(price/MD_{t-1})^4)`. Self-adjusting MA that tracks price closely. pandas-ta `mcgd`.

**Common edge cases for all:** EMA-seeding inheritance, long warmup for cascades (T3), `sum(volume)=0` guard (VWMA), and division guards in self-referential forms (McGinley, VIDYA).
