# Technical-Analysis Indicator Library — Master Index

A modular, pure-Python, **one-class-per-indicator** library. Documentation-first: each indicator has its own `.md` spec (10 sections) under a category folder. Build `base/` first — almost everything composes from it.

**Start here:** [`CONVENTIONS.md`](CONVENTIONS.md) — class design, universal edge-case policy, build order, testing.

| Category | Folder | Index | Scope |
|----------|--------|-------|-------|
| Base components | `base/` | [base/README](base/README.md) | SMA, EMA, WMA, RMA, stdev, True Range |
| Trend & MAs | `trend/` | [trend/README](trend/README.md) | ~55 MAs + directional/trend systems |
| Momentum | `momentum/` | [momentum/README](momentum/README.md) | ~45 oscillators |
| Volatility | `volatility/` | [volatility/README](volatility/README.md) | ~20 band/vol indicators |
| Volume | `volume/` | [volume/README](volume/README.md) | ~22 volume indicators |
| Statistics | `statistics/` | [statistics/README](statistics/README.md) | regression, correlation, moments |
| Cycle | `cycle/` | [cycle/README](cycle/README.md) | Hilbert Transform family |
| Price transform | `price_transform/` | [price_transform/README](price_transform/README.md) | hl2, hlc3, OHLC4, Heikin-Ashi |
| Candles | `candles/` | [candles/README](candles/README.md) | 61 CDL patterns |
| Math transform | `math_transform/` | [math_transform/README](math_transform/README.md) | vector math & operators |
| Utils | `utils/` | [utils/README](utils/README.md) | crossover/lag/decay helpers |

## Fully-written detailed specs in this drop
- **base/**: SMA, EMA, WMA, RMA (Wilder), True Range, Rolling Stdev
- **trend/**: MACD, KAMA, Supertrend, Parabolic SAR, ADX/DMI, Ichimoku, DEMA/TEMA, HMA, TRIX, Aroon, Vortex, PPO, KST (+ misc_MA catalog)
- **momentum/**: RSI, Stochastic, StochRSI, Williams %R, CCI, TSI, Ultimate Oscillator, Connors RSI, Fisher (+ misc_momentum catalog)
- **volatility/**: Bollinger, ATR/NATR, Keltner, Donchian, Ulcer (+ misc_volatility catalog)
- **volume/**: OBV, ADL/CMF/Chaikin, MFI, VWAP (+ misc_volume catalog)
- **statistics/**: Linear Regression family (+ misc_statistics catalog)
- **cycle/**: Hilbert Transform family (all six)
- **price_transform/**: all six transforms incl. Heikin-Ashi
- **candles/**: full 61-pattern catalog + scoring contract
- **math_transform/**, **utils/**: full catalogs

The category `README.md` files list **every** indicator in scope (190+), so the full catalog is captured even where a dedicated per-indicator file isn't written yet. The `misc_*.md` files hold concise but real specs (formula + edge cases + library refs) for the remaining indicators, ready to split into individual class files.

## Reference libraries surveyed
TA-Lib (158 functions incl. 61 candlestick patterns), pandas-ta / pandas-ta-classic (192 indicators + 62 CDL = 252 unique), Tulip Indicators (104), finta (~80), bukosabino/ta (43, the class-per-indicator analog), QTPyLib, freqtrade/technical.
