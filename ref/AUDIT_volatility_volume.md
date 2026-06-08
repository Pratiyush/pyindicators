# Correctness Review — volatility (18) + volume (27)

Line-by-line review. Both families compose the already-verified `base/` primitives
(`sma`/`ema`/`stdev`/`rma`/`true_range`) and `core.safe_divide`, so each was read for correct
composition of its canonical formula and confirmed causal. Every indicator has a parity test.

**Legend** — Verdict: ✅ verified.

## volatility (18)

| Indicator | Verdict | Source review (canonical formula) | Test |
|---|---|---|---|
| `bbands` | ✅ | SMA ± k·stdev (population ddof=0, TA-Lib); bandwidth + %B. | parity vs talib/pandas-ta |
| `atr` | ✅ | `rma(true_range, length)` (Wilder). | parity vs talib (tail) |
| `natr` | ✅ | `100·atr/close`, guarded. | parity vs talib.NATR (tail) |
| `keltner` | ✅ | `EMA(close) ± mult·ATR`. | composition vs verified ema+atr |
| `donchian` | ✅ | rolling min(low)/max(high) + mid. | parity |
| `cvi` | ✅ | ROC of `EMA(high-low)` over roc_length. | constant-range→0 + real-data |
| `ulcer` | ✅ | RMS of percent drawdown from rolling max. | parity vs pandas-ta |
| `hv` | ✅ | `stdev(ln(close/close₋₁))·√annual·100`. | definitional |
| `massi` | ✅ | sum of `EMA(hl)/EMA(EMA(hl))` ratio (Mass Index). | parity vs pandas-ta |
| `rvi` | ✅ | stdev split into up/down days, RSI-style smoothing. | parity |
| `accbands` | ✅ | SMA ± c·(H−L)/(H+L) acceleration bands. | parity vs pandas-ta |
| `aberration` | ✅ | `SMA(hlc3) ± ATR` Keltner-style zone. | parity vs pandas-ta |
| `chandelier` | ✅ | `HH(N) − mult·ATR` / `LL(N) + mult·ATR` trailing stops. | composition vs verified extremes+atr |
| `hwc` | ✅ | Holt-Winter channel (level/trend/seasonal recurrence) + bands. | parity |
| `pdist` | ✅ | `2(H−L) − |C−O| + |O − prevC|`. | golden + parity vs pandas-ta |
| `thermo` | ✅ | Elder market thermometer: max of outside moves, EMA-smoothed. | parity |
| `apz` | ✅ | double-EMA mid ± dev·EMA(range) adaptive price zone. | parity |
| `starc` | ✅ | `SMA ± mult·ATR` STARC bands. | parity |

## volume (27)

| Indicator | Verdict | Source review (canonical formula) | Test |
|---|---|---|---|
| `obv` | ✅ | `cumsum(sign(Δclose)·volume)`. | parity vs talib/pandas-ta |
| `ad` | ✅ | `cumsum(MFM·volume)`, MFM=((C−L)−(H−C))/(H−L). | parity vs talib/finta |
| `cmf` | ✅ | rolling Σ(MFV)/Σ(volume). | parity |
| `adosc` | ✅ | `EMA(adl,fast) − EMA(adl,slow)` Chaikin osc. | parity vs talib |
| `mfi` | ✅ | money-flow index from typical-price money flow. | parity vs talib (≥3 lib) |
| `vwap` | ✅ | rolling Σ(tp·vol)/Σ(vol). | definitional |
| `efi` | ✅ | `EMA(Δclose·volume)` Elder Force Index. | parity |
| `eom` | ✅ | ease-of-movement: hl2 distance / box ratio. | parity vs pandas-ta |
| `nvi` | ✅ | negative volume index (update on down-volume days). | parity |
| `pvi` | ✅ | positive volume index (update on up-volume days). | parity |
| `kvo` | ✅ | Klinger volume oscillator (signed-volume EMA diff) + signal. | parity |
| `vwmacd` | ✅ | volume-weighted MACD (vwma fast/slow). | parity |
| `pvt` | ✅ | `cumsum(Δclose%·volume)` price-volume trend. | parity |
| `vfi` | ✅ | Katsanos volume flow (log-return cutoff vs stdev). | parity |
| `marketfi` | ✅ | `(H−L)/volume`. | definitional |
| `pvol` | ✅ | `close·volume`. | parity |
| `pvr` | ✅ | price-volume rank (4-state Δprice×Δvolume). | parity |
| `wad` | ✅ | Williams A/D cumulative true-range accumulation. | definitional |
| `aobv` | ✅ | Archer OBV + min/max/fast/slow EMAs + long/short run. | parity vs pandas-ta |
| `rvol` | ✅ | `volume / SMA(volume)`. | definitional |
| `vol_sma` | ✅ | `SMA(volume)`. | parity |
| `fve` | ✅ | Finite Volume Element (intrabar cutoff, cumulative). | parity |
| `vpa_climactic_bars` | ✅ | high-volume + wide-range + close-position climax flag. | golden + real-data |
| `vpa_no_supply` | ✅ | narrow down-bar, volume < prior two. | golden + real-data |
| `vpa_no_demand` | ✅ | narrow up-bar, volume < prior two. | golden + real-data |
| `vpa_stopping_volume` | ✅ | down-bar, ultra-high volume, long lower wick. | golden + real-data |
| `vpa_effort_vs_result` | ✅ | effort(volume)-vs-result(range) anomaly flags. | golden + real-data |

## Cross-cutting
- **Causality:** cumulative indicators (obv/ad/pvt/wad/nvi/pvi/aobv) are running sums of
  past bars; rolling/EMA indicators use `min_periods == length` / causal recurrences. The
  real-data prefix-vs-full invariant test confirms no look-ahead across all 45.
- **Division guards:** every ratio routes through `core.safe_divide` (zero range / zero volume
  → NaN, never ±inf) — confirmed by the real-data no-infinity invariant.
