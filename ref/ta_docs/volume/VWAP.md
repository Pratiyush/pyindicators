# VWAP — Volume Weighted Average Price

- **Category:** volume / overlap

## 1. What it measures
The average price weighted by volume over a session — the institutional "fair value" benchmark.

## 2. How it works / formula
```
TP   = (High + Low + Close) / 3
VWAP = cumulative sum(TP * Volume) / cumulative sum(Volume)   # RESET each session
```

## 3. Parameters / best settings
- Session-anchored (daily reset) is standard; "rolling VWAP" over N bars is an alternative.

## 4. Outputs & interpretation
- Price above VWAP = bullish intraday bias; used as execution benchmark and mean-reversion anchor.

## 5. Edge cases
- **Requires a DatetimeIndex and per-session reset** or it drifts indefinitely.
- **sum(Volume)=0** → guard /0.

## 6. Pitfalls
- **Lookahead risk:** a naive cumulative VWAP that isn't anchored is implicitly forward-looking in some framings; freqtrade disabled plain `vwap()` in favor of `rolling_vwap()`. Anchor and reset correctly.

## 7. References & libraries
- pandas-ta `vwap`; freqtrade/technical `rolling_vwap`; QTPyLib `vwap`. (Not in core TA-Lib.)
