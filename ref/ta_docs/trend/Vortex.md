# Vortex Indicator (VI+ / VI-)

- **Category:** trend
- **Authors:** Etienne Botes & Douglas Siepman (2010)
- **Default:** period 14

## 1. What it measures
Two oscillating lines capturing positive and negative trend movement; crossovers identify the start of new trends.

## 2. How it works
Relate the distance between today's high/low and yesterday's opposite extreme to the true range.

## 3. Algorithm & formula
```
VM+ = abs(High_t - Low_{t-1})
VM- = abs(Low_t  - High_{t-1})
VI+ = sum(VM+, N) / sum(TR, N)
VI- = sum(VM-, N) / sum(TR, N)
```

## 4. Parameters / best settings
- `N=14` (also 21–34 for smoother).

## 5. Outputs & interpretation
- VI+ crossing above VI- = bullish trend start; below = bearish.

## 6. Edge cases
- **sum(TR)=0** (flat, no gaps) → guard /0.
- Warmup N bars.

## 7. Pitfalls
- Using close-to-close instead of the cross high/low terms.

## 8. References & libraries
- pandas-ta `vortex`; tulip `vi`? (no) — finta `VORTEX`; bukosabino/ta `VortexIndicator`. (Not in core TA-Lib.)
