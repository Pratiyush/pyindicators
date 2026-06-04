# pyindicators — backlog (deferred / out-of-scope-for-now)

These items came out of the research gap-analysis but are **not** plain per-symbol OHLCV
indicators, so they don't belong in this library's core contract today. They're recorded here
as a tracked backlog — most belong in the **Stock-Finder app / screener** (which has the
universe, fundamentals, and benchmark data), or in a **future dedicated sub-module** of this
library (a different base class than the 1:1 time-aligned `Indicator`).

Status legend: 🅰️ app/screener · 🅱️ future pyindicators sub-module (needs a new base class) · ❓ research.

## Market breadth / internals — 🅰️ app (needs the whole universe)
| item | note |
|------|------|
| Advance-Decline Line | cumulative advancing − declining issues across the universe |
| McClellan Oscillator + Summation Index | EMAs of net advances/declines |
| Arms Index (TRIN) | (adv/decl) / (up-vol/down-vol) |
| Diffusion / % above MA / new-highs-new-lows | breadth participation across the universe |
| Follow-Through Day (O'Neil) | index-level price + volume confirmation |

## Cross-symbol / relative-to-benchmark — 🅱️ sub-module (two series)
| item | note |
|------|------|
| `rs_line` (price relative) | close / benchmark_close — needs a benchmark series |
| `mansfield_rs` | normalised RS line vs its MA — needs a benchmark |
| Beta / Correlation / Covariance vs benchmark | already have rolling `correl`/`beta`/`covariance` planned on two columns; a benchmark-aware variant is a sub-module |
| Pairs / cointegration / Kalman hedge ratio | two-symbol statistical arbitrage |

## Fundamentals — 🅰️ app (not derivable from OHLCV)
P/E, PEG, P/S, P/B, ROE (DuPont), EPS growth (q/yoy/fwd), FCF & FCF-margin, debt/equity,
current ratio, margins, asset turnover, sales growth, insider %, R&D% , CAPE/Shiller. Feed
cross-sectional value/quality/growth z-scores in the screener.

## Sentiment / external feeds — 🅰️ app
VIX, put/call ratio, COT positioning percentile, news/social NLP sentiment.

## Subjective chart patterns — 🅱️ sub-module (need pivot/trendline detection)
Head-and-shoulders, double top/bottom, triangles (asc/desc/sym), wedges, flag, pennant,
cup-with-handle, high-tight-flag, measured move, rectangle, rounding bottom. Require swing-pivot
and trendline fitting (and care to stay causal) — a dedicated pattern engine, not a per-bar indicator.

## Harmonic & wave patterns — 🅱️ sub-module / ❓
Gartley, Butterfly, Bat, Crab, Cypher (Carney), Elliott Wave. Subjective Fibonacci-ratio /
wave labelling; low automatability.

## Fibonacci / pivot levels — 🅱️ sub-module (prior-session lookback or swing pivots)
Fibonacci retracement / extension, PRZ confluence, classic/Woodie/Camarilla/DeMark pivot points
(a per-bar causal `pivots` is already a TARGET; the multi-variant + fib levels are the backlog part),
support/resistance zones, market-phase classifier, supply/demand order blocks.

## Backtesting / methodology gates — 🅰️ app (Phase 4 backtester)
White's Reality Check, walk-forward, Monte-Carlo permutation, purged/embargoed CV, pyfolio-style
metrics, position sizing (half-Kelly). These are the strategy-validation layer, not indicators.

---

## Remaining in-scope build sequence (43 of 316 unbuilt as of 273/316)

Evaluation by **utility × feasibility × effort**, in recommended build order. Groups 1–5 fit (or
nearly fit) the core `Indicator` contract; group 6 needs a different contract → stays backlog.

**1. Quick wins — oracle-backed, trivial (~30 min):**
- `minmax`, `minmaxindex` (math_transform, 2 outputs) — TA-Lib MINMAX/MINMAXINDEX exact. (Missed in the math wave.)
- `ttm_squeeze` (momentum) — almost certainly an alias/thin variant of the built `squeeze`; verify vs pandas-ta, else register as alias.

**2. High-utility primitives — need a small framework decision (do early, they unblock strategies):**
- `crossover`, `crossunder`, `crossany`, `cross_value`, `lag`, `percent_rank`, `roc1` — core signal/series helpers (HIGH utility). `decay`, `edecay` — low utility.
- *Issue:* these take a single series / two series / series+threshold, not an OHLCV frame. Add a lightweight series-transform contract (or ship them as a `utils` functions module + thin registry wrappers where a close-based form makes sense). Decide the contract first, then each is trivial.

**3. Real indicators — attended, oracle-backed (moderate–hard):**
- `mama` + `fama` (trend) — TA-Lib MAMA (one call → both); Hilbert-based, finicky exact parity (reverse-engineer like the candle helper). Medium utility, high effort.
- `td_seq` (momentum) — TD Sequential setup/countdown; pandas-ta oracle; multi-rule, medium-high effort, popular.
- `rainbow` (trend) — recursive SMA cascade + bands; check finta/pandas-ta oracle; low-med effort.

**4. VSA / price-action — golden-only (no parity oracle; define rules carefully):**
- `vpa_climactic_bars`, `vpa_no_supply`, `vpa_no_demand`, `vpa_stopping_volume`, `vpa_effort_vs_result` (volume) — VSA bar flags (Williams/Coulling); 0/1 outputs, golden-validated.
- `spring`, `upthrust`, `big_shadow`, `kangaroo_tail`, `wammie`, `moolah` (candles) — Wyckoff/price-action; no TA-Lib oracle; golden-only; low-med utility.

**5. Hilbert cycle — hardest exact-parity, lowest everyday utility (do last, or skip):**
- `ht_dcperiod`, `ht_dcphase`, `ht_phasor`, `ht_sine`, `ht_trendmode`, `ht_trendline` — TA-Lib HT_* exact oracles but the Hilbert Transform is TA-Lib's finickiest parity. Best: one agent cracks a shared HT helper (candle-foundation style), then the 6 reuse it.
- `ebsw`, `dsp`, `msw` — Ehlers cycle (pandas-ta/Ehlers); moderate.

**6. Different contract → stays backlog (NOT per-bar single-symbol OHLCV):**
- `rs_line`, `mansfield_rs` (relative) — need a **benchmark/index** series → 🅰️ app/screener (or a 2-input relative-strength contract). HIGH utility, wrong layer.
- `renko`, `kagi`, `three_line_break` (structure) — chart-type transforms that **resample bars** (output not 1:1 with input) → 🅱️ chart-transform sub-module.
- `vp` (volume profile) — bins volume by price level (histogram, not a per-bar series) → 🅱️ sub-module.
- `gsv` (volatility) — definition/oracle unclear → ❓ research the exact spec before building.

---
_When the app/screener phase resumes, pull from this backlog. Items needing only a new base
class (🅱️) can graduate into pyindicators later (e.g. a `CrossSectionalIndicator` for breadth /
relative strength, or a `PatternIndicator` for chart patterns)._
