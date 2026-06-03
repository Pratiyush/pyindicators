# pyindicators

**Modular, look-ahead-safe technical-indicator library for pandas/numpy.**

Every indicator is a small, composable unit that computes over a canonical OHLCV frame and
returns a frame aligned 1:1 to the input. Indicators are **causal by construction**
(trailing-only windows, no centered windows or negative shifts), validated by a
truncation-invariance test, and discoverable through a plugin registry.

## Install

```bash
pip install pyindicators        # once published
# or, from source:
pip install git+https://github.com/Pratiyush/pyindicators
```

## Quickstart

```python
import pandas as pd
import pyindicators as pyi

# canonical OHLCV: columns [ts, open, high, low, close, close_raw, volume, adj_factor]
df = ...

rsi = pyi.INDICATORS.create("rsi", period=14)
out = rsi.compute(df)                      # -> DataFrame with column "rsi"

# compose many indicators into one feature frame (parametrized column names)
feats = pyi.build_features(df, ["sma:period=50", "sma:period=200", "rsi:period=14"])
# feats has sma_50, sma_200, rsi_14 joined onto df

# multi-timeframe, no look-ahead
weekly = pyi.resample_ohlcv(df, pyi.Timeframe.WEEK, base=pyi.Timeframe.DAY)
```

## Indicators

List them at runtime:

```python
import pyindicators as pyi
print(pyi.INDICATORS.names())
```

Families: **trend** (sma, ema, wma, sma_slope, macd, adx, aroon, kama, hma), **momentum**
(rsi, roc, momentum, stoch, cci, willr), **volatility** (atr, bbands, keltner, stdev,
ttm_squeeze), **volume** (obv, vwap, rvol, vol_sma, mfi, force_index, adl, cmf, williams_ad),
**structure** (rolling_high/low, donchian, pct_from_high/low), **relative**
(rs_line, mansfield_rs, rs_rating), **vortex** — and growing.

## Design

- `Indicator.compute(df) -> df` (same index, columns == `outputs`); params validated by pydantic.
- `INDICATORS` registry + `@INDICATORS.register("name")` for plug-and-play discovery.
- `build_features` / `parse_spec` to compose indicators by `"name:param=value"` spec.
- `resample_ohlcv` + `align_to_base` for causal multi-timeframe features.

## License

MIT © Pratiyush
