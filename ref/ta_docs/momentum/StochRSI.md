# Stochastic RSI

- **Category:** momentum oscillator (composite)
- **Author:** Chande & Kroll (1994)
- **Default:** RSI 14, Stoch 14, %K 3, %D 3

## 1. What it measures
A stochastic applied to RSI values instead of price — a more sensitive, faster overbought/oversold oscillator.

## 2. How it works
Compute RSI, then run the stochastic normalization on the RSI series.

## 3. Algorithm & formula
```
r = RSI(close, rsi_len)
StochRSI = (r - min(r, stoch_len)) / (max(r, stoch_len) - min(r, stoch_len))
%K = SMA(StochRSI*100, k) ; %D = SMA(%K, d)
```

## 4. Parameters / best settings
- 14/14/3/3 (classic). Smaller = noisier.

## 5. Outputs & interpretation
- 0–1 (or 0–100); >0.8 overbought, <0.2 oversold; very fast → many signals.

## 6. Edge cases
- **max(r)=min(r)** over the window → division by zero → guard.
- Double warmup (RSI warmup + stoch window).

## 7. Pitfalls
- Applying stochastic to price (that's just Stochastic) instead of to RSI.

## 8. References & libraries
- TA-Lib `STOCHRSI`; pandas-ta `stochrsi`; bukosabino/ta `StochRSIIndicator`.
