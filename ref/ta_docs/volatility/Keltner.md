# Keltner Channels

- **Category:** volatility / overlap
- **Authors:** Chester Keltner (original); Linda Raschke (modern ATR version)
- **Defaults (modern):** EMA 20, ATR 10, multiplier 2

## 1. What it measures
A volatility envelope around an EMA using ATR for band width (smoother than Bollinger, which uses stdev).

## 2. How it works / formula
```
# Modern (ATR) version:
Middle = EMA(close, 20)
Upper  = Middle + mult * ATR(10)
Lower  = Middle - mult * ATR(10)

# Original (Keltner) version:
Middle = SMA(typical price, N)
band   = SMA(High - Low, N)
Upper/Lower = Middle +/- band
```

## 3. Parameters / best settings
- Modern 20/10/2. Expose an `original_version` flag (as bukosabino/ta does).

## 4. Outputs & interpretation
- Breakouts beyond bands = momentum; pairs with Bollinger for the "squeeze".

## 5. Edge cases
- Inherits EMA + ATR warmup/seed conventions.

## 6. Pitfalls
- Mixing original vs modern definitions silently.

## 7. References & libraries
- pandas-ta `kc`; finta `KC`; bukosabino/ta `KeltnerChannel`. (Not in core TA-Lib.)
