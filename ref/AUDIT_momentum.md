# Correctness Review — momentum (52)

Line-by-line review of the momentum family. Each composes verified `base/` primitives
(`rma`/`ema`/`sma`/`stdev`) or a documented numeric recurrence, was read against its canonical
formula, and is parity-tested (TA-Lib / pandas-ta where they ship it). Causality confirmed by
the real-data prefix-vs-full invariant; bounded oscillators respect their declared bounds.

**Legend** — Verdict: ✅ verified.

## RSI / Stochastic family (13)

| Indicator | Verdict | Formula |
|---|---|---|
| `rsi` | ✅ | Wilder `100−100/(1+RMA(gain)/RMA(loss))` — parity vs talib (≥3 lib) |
| `rsx` | ✅ | Jurik RSX (smoothed RSI, numeric loop) |
| `crsi` | ✅ | Connors RSI = avg(RSI(3), RSI(streak,2), percentrank(roc1)) |
| `stochrsi` | ✅ | stochastic of RSI, %K/%D |
| `rsi_positive_reversal` | ✅ | Cardwell: strict 3-bar RSI trough with higher price |
| `rsi_negative_reversal` | ✅ | Cardwell: strict 3-bar RSI peak with lower price |
| `stoch` | ✅ | `%K=100·(C−LL)/(HH−LL)` smoothed, `%D=SMA(%K)` — parity vs talib |
| `stochf` | ✅ | fast stochastic (unsmoothed %K) |
| `kdj` | ✅ | stochastic K/D + `J=3K−2D` |
| `smi` | ✅ | SMI ergodic (double-smoothed relative range) |
| `willr` | ✅ | `−100·(HH−C)/(HH−LL)` — parity vs talib (≥3 lib) |
| `uo` | ✅ | Ultimate Oscillator (3-period weighted BP/TR) |
| `demarker` | ✅ | DeMarker `SMA(DeMax)/(SMA(DeMax)+SMA(DeMin))` |

## ROC / price-change family (8)

| Indicator | Verdict | Formula |
|---|---|---|
| `roc` | ✅ | `100·(C/C₋ₙ −1)` — parity vs talib (≥3 lib) |
| `rocp` | ✅ | `(C−C₋ₙ)/C₋ₙ` |
| `rocr` | ✅ | `C/C₋ₙ` |
| `rocr100` | ✅ | `100·C/C₋ₙ` |
| `mom` | ✅ | `C−C₋ₙ` — parity vs talib (≥3 lib) |
| `slope` | ✅ | `C.diff(length)` (per-bar slope) |
| `bias` | ✅ | `100·(C−SMA)/SMA` deviation |
| `disparity_index` | ✅ | `100·(C−SMA)/SMA` (Nison/Pring) — definitional |

## Oscillators & indices (18)

| Indicator | Verdict | Formula |
|---|---|---|
| `cci` | ✅ | `(tp−SMA(tp))/(0.015·MAD)` (mean-abs-dev) — parity vs talib (≥3 lib) |
| `cmo` | ✅ | Chande momentum osc (pandas-ta simple-sum convention, documented) |
| `coppock` | ✅ | `WMA(ROC(long)+ROC(short))` |
| `tsi` | ✅ | double-EMA-smoothed momentum ratio + signal |
| `pvo` | ✅ | percentage volume osc (PPO on volume) |
| `fisher` | ✅ | Fisher transform of normalized price + signal |
| `laguerre_rsi` | ✅ | Ehlers Laguerre filter RSI (gamma) |
| `cfo` | ✅ | Chande forecast osc `100·(C−TSF)/C` |
| `fosc` | ✅ | forecast osc `100·(C−TSF₋₁)/C` |
| `cg` | ✅ | Ehlers center-of-gravity |
| `pgo` | ✅ | Pretty Good Osc `(C−SMA)/EMA(TR)` |
| `psl` | ✅ | psychological line `100·count(up)/N` |
| `rsl` | ✅ | Levy relative strength `C/SMA` |
| `rvgi` | ✅ | relative vigor index (SWMA num/den) + signal |
| `inertia` | ✅ | RVI smoothed by linear regression |
| `cti` | ✅ | Ehlers correlation-trend index |
| `derivative_osc` | ✅ | double-smoothed RSI derivative + signal |
| `er` | ✅ | Kaufman efficiency ratio `|ΔC|/Σ|ΔC|` |

## TTM / Bill Williams / DeMark / composites (13)

| Indicator | Verdict | Formula |
|---|---|---|
| `squeeze` | ✅ | TTM squeeze: BB-in-KC flags + `SMA(MOM)` momentum |
| `squeeze_pro` | ✅ | TTM squeeze pro (wide/normal/narrow KC bands) |
| `ttm_momentum` | ✅ | `linreg(C − (donchian_mid+SMA)/2)` — composition verified |
| `stc` | ✅ | Schaff trend cycle (double-stochastic of MACD) |
| `qqe` | ✅ | QQE (RSI-MA + ATR-trailing bands, numeric loop) |
| `alligator` | ✅ | 3 Wilder-smoothed (`rma`) median lines (jaw/teeth/lips) |
| `gator` | ✅ | gator osc `|jaw−teeth|`, `−|teeth−lips|` |
| `ao` | ✅ | awesome osc `SMA(hl2,5)−SMA(hl2,34)` |
| `eri` | ✅ | Elder Ray bull/bear power vs EMA |
| `bop` | ✅ | balance of power `(C−O)/(H−L)` — parity vs talib (≥3 lib) |
| `brar` | ✅ | AR/BR sentiment ratios |
| `td_seq` | ✅ | DeMark sequential setup counts (run-length) |
| `cmb_composite_index` | ✅ | Brown composite: `RSI.diff(mom) + SMA(RSI(short))` — composition verified |

## Cross-cutting
- **Causality:** numeric-loop indicators (rsx, qqe, crsi streaks) iterate strictly forward over
  past bars; all others compose causal primitives. Verified by the real-data prefix-vs-full test.
- **Bounds:** RSI/StochRSI/%K/%D/Williams/DeMarker/PSL respect their declared 0–100 (or −100–0)
  bounds — asserted by the real-data invariants sweep.
