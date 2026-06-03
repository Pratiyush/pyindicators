# base/ — Reusable Core Components

These are **not** standalone "indicators" you plot for signals; they are the shared primitives that the rest of the library composes from. Build and test these **first** to floating-point parity with TA-Lib, because a bug here propagates everywhere.

| File | Component | Reused by |
|------|-----------|-----------|
| `SMA.md` | Simple Moving Average | Bollinger, TRIMA, Stochastic %D, CMF window, KST |
| `EMA.md` | Exponential Moving Average | MACD, PPO, TRIX, TSI, Chaikin Osc, KVO, Keltner, DEMA/TEMA/T3 |
| `WMA.md` | Weighted Moving Average | HMA, Coppock |
| `RMA.md` | Wilder's Smoothing / SMMA | RSI, ATR, ADX/DMI, +DM/-DM |
| `TrueRange.md` | True Range | ATR, NATR, Supertrend, Keltner, Chandelier, UO, Vortex |
| `RollingStdev.md` | Rolling stdev / variance | Bollinger, z-score, RVI |

**Design rule:** every downstream class must compose these — never reimplement an EMA/ATR/RMA inline.
