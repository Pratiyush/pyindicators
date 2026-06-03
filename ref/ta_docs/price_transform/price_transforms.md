# Price Transforms (AVGPRICE, MEDPRICE, TYPPRICE, WCLPRICE, OHLC4, Heikin-Ashi)

- **Category:** price_transform

## Single-bar transforms
```
AVGPRICE  = (Open + High + Low + Close) / 4
MEDPRICE  = (High + Low) / 2                  # "hl2"
TYPPRICE  = (High + Low + Close) / 3          # typical price, "hlc3"
WCLPRICE  = (High + Low + 2*Close) / 4        # weighted close, "wcp"
OHLC4     = (Open + High + Low + Close) / 4   # == AVGPRICE
```
TA-Lib: `AVGPRICE`, `MEDPRICE`, `TYPPRICE`, `WCLPRICE`. tulip: `avgprice`, `medprice`, `typprice`, `wcprice`. pandas-ta: `hl2`, `hlc3`, `ohlc4`, `wcp`.

## Heikin-Ashi (HA)
```
HA_Close = (Open + High + Low + Close) / 4
HA_Open  = (HA_Open_{t-1} + HA_Close_{t-1}) / 2    # seed: (Open_0 + Close_0)/2
HA_High  = max(High, HA_Open, HA_Close)
HA_Low   = min(Low,  HA_Open, HA_Close)
```
Smoothed candles that filter noise; consecutive same-color candles = trend persistence. pandas-ta `ha`; finta `HEIKIN_ASHI`.

## Edge cases
- HA_Open is recursive — seed it explicitly at bar 0 or the whole series shifts.
- These are exact (no warmup) except HA (needs its seed).
