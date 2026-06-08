# Correctness Review — trend (61)

Line-by-line review of the trend family: moving-average variants, the MACD and DMI/ADX
families, parabolic SAR, and trend systems. Each composes verified `base/` primitives or a
documented recurrence, was read against its canonical formula, and is parity-tested (TA-Lib /
pandas-ta where they ship it). Causality confirmed by the real-data prefix-vs-full invariant
(SAR/Supertrend/PMax are path-dependent but strictly backward-looking).

**Legend** — Verdict: ✅ verified.

## Moving averages (26)

| Indicator | Verdict | Formula | Indicator | Verdict | Formula |
|---|---|---|---|---|---|
| `dema` | ✅ | 2·EMA−EMA(EMA) | `tema` | ✅ | 3·EMA−3·EMA²+EMA³ |
| `trima` | ✅ | SMA of SMA (triangular) | `kama` | ✅ | Kaufman adaptive (ER-scaled α) |
| `hma` | ✅ | WMA(2·WMA(n/2)−WMA(n), √n) | `vwma` | ✅ | Σ(close·vol)/Σ(vol) |
| `alma` | ✅ | Gaussian-weighted (offset/sigma) | `zlma` | ✅ | EMA of de-lagged price |
| `t3` | ✅ | Tillson 6×EMA (vfactor) | `frama` | ✅ | fractal-dimension adaptive α |
| `vidya` | ✅ | CMO-volatility adaptive EMA | `fwma` | ✅ | Fibonacci-weighted MA |
| `sinwma` | ✅ | sine-weighted MA | `swma` | ✅ | symmetric-weighted MA |
| `pwma` | ✅ | Pascal-triangle-weighted MA | `hwma` | ✅ | Holt-Winter (na/nb/nc) |
| `jma` | ✅ | Jurik adaptive smoothing | `mcgd` | ✅ | McGinley dynamic |
| `mama` | ✅ | MESA adaptive (Hilbert phase) | `fama` | ✅ | following adaptive MA |
| `ssf` | ✅ | Ehlers super-smoother (2/3-pole) | `vama` | ✅ | volume-adjusted MA |
| `evwma` | ✅ | elastic volume-weighted MA | `lsma` | ✅ | linear-regression endpoint MA |
| `hilo` | ✅ | Gann HiLo activator | `rainbow` | ✅ | recursive SMA cascade (2..10) |

## MA derivatives & MACD/oscillator family (10)

| Indicator | Verdict | Formula |
|---|---|---|
| `sma_slope` | ✅ | `SMA(close).diff()` |
| `ma_spread` | ✅ | `SMA(fast) − SMA(slow)` |
| `macd` | ✅ | `EMA(fast) − EMA(slow)`, signal EMA, hist — parity vs talib (≥3 lib) |
| `macdext` | ✅ | MACD with selectable MA types |
| `macdfix` | ✅ | MACD fixed 12/26 |
| `ppo` | ✅ | `100·(EMA_fast−EMA_slow)/EMA_slow` |
| `apo` | ✅ | `EMA_fast − EMA_slow` (absolute) |
| `trix` | ✅ | 1-bar ROC of triple-EMA — parity vs talib (≥3 lib) |
| `kst` | ✅ | weighted sum of 4 smoothed ROCs + signal |
| `dpo` | ✅ | causal `close − SMA(N).shift(N//2+1)` (non-centered, no look-ahead) |

## DMI / ADX family (9)

| Indicator | Verdict | Formula |
|---|---|---|
| `plus_dm` / `minus_dm` | ✅ | Wilder directional movement (up-move/down-move dominance) |
| `plus_di` / `minus_di` | ✅ | `100·RMA(±DM)/ATR` |
| `dx` | ✅ | `100·|+DI−−DI|/(+DI+−DI)` |
| `adx` | ✅ | `RMA(DX)` — parity vs talib (≥3 lib, tail) |
| `adxr` | ✅ | `(ADX + ADX.shift(length))/2` |
| `aroon` / `aroon_osc` | ✅ | bars-since-rolling-extreme (latest-tie convention) |

## Trend systems & misc (16)

| Indicator | Verdict | Formula |
|---|---|---|
| `psar` | ✅ | parabolic SAR recurrence (AF 0.02→0.2) — parity vs talib |
| `sarext` | ✅ | extended SAR (separate long/short AF + offset) |
| `supertrend` | ✅ | ATR bands with carry-forward flip (path-dependent, causal) |
| `ichimoku` | ✅ | tenkan/kijun/span A/B from rolling H/L midpoints |
| `vortex` | ✅ | `Σ|VM±|/ΣTR` — parity (≥3 lib) |
| `chop` | ✅ | choppiness `100·log10(ΣTR/range)/log10(N)` |
| `vhf` | ✅ | vertical-horizontal filter `(HH−LL)/Σ|Δclose|` |
| `cksp` | ✅ | Chande-Kroll stop (ATR-based) |
| `qstick` | ✅ | `SMA(close−open)` |
| `ttm_trend` | ✅ | close vs 6-bar hl2 average (bias) |
| `increasing` / `decreasing` | ✅ | `close.diff(length) > 0` / `< 0` |
| `amat` | ✅ | Archer MA trends (long_run/short_run of fast/slow MAs) |
| `pmax` | ✅ | profit-maximizer ATR trailing (path-dependent, causal) |
| `pivots` | ✅ | floor-trader pivot + R1/R2/R3/S1/S2/S3 |
| `long_run` / `short_run` | ✅ | bullish/bearish regime flags — parity vs pandas-ta |
