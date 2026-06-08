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

## Deferred items (10) — the in-scope catalog is 306/306 built & Done (100%)

The full in-scope catalog is built **and Done** (golden + parity tests): all base /
price_transform / trend / momentum / volatility / volume / statistics / cycle / math_transform /
utils indicators, the 61 TA-Lib candles, the Hilbert HT_* family, MAMA/FAMA, TD Sequential, the
VSA/Wyckoff bars, and the crossover signal helpers — 100% line+branch coverage, audit 0
correctness failures. The 10 items below are **deferred by design** (they need a different
contract than the per-bar 1:1 `Indicator` base), not "unbuilt"; they are listed in the
`## Deferred` section of `docs/TRACKING.md` and excluded from the in-scope total.

The **10 remaining** do not fit the core per-bar single-symbol `Indicator` contract, or lack a
defensible spec. They split into "won't build as-is" and "needs a new contract first":

**A. Won't build as registered indicators (duplicate / ill-defined):**
- `ttm_squeeze` (momentum) — duplicate of the built `squeeze` (TTM Squeeze *is* `squeeze`). Leave as a documented alias of `squeeze`; do not add a second implementation.
- `wammie`, `moolah` (candles) — no authoritative definition or oracle anywhere (TA-Lib / pandas-ta / finta / ta). Too ill-defined to validate. Drop unless a concrete spec surfaces.

**B. Needs a different contract → graduate later (NOT per-bar single-symbol OHLCV):**
- `rs_line`, `mansfield_rs` (relative) — require a **benchmark/index** series, so they belong to a 2-input relative-strength contract (`CrossSectionalIndicator`) or the 🅰️ app/screener layer. HIGH utility, wrong layer for the 1:1 `Indicator` base.
- `renko`, `kagi`, `three_line_break` (structure) — chart-type transforms that **resample bars**; output is not 1:1 with the input index → 🅱️ chart-transform sub-module with its own base class.
- `vp` (volume profile) — bins volume by price level (a histogram, not a per-bar series) → 🅱️ sub-module.
- `gsv` (volatility) — exact definition/oracle still unclear → ❓ research the spec before building.

**Recommended sequence when picked up:** (1) register `ttm_squeeze` as an alias of `squeeze`
(trivial, closes 1 item); (2) build the `CrossSectionalIndicator` base, then `rs_line` +
`mansfield_rs` (HIGH utility, unblocks relative-strength screening); (3) add the chart-transform
sub-module base, then `renko` / `kagi` / `three_line_break` / `vp`; (4) research `gsv`, build or
formally drop; (5) drop `wammie` / `moolah` unless a spec surfaces.

---
_When the app/screener phase resumes, pull from this backlog. Items needing only a new base
class (🅱️) can graduate into pyindicators later (e.g. a `CrossSectionalIndicator` for breadth /
relative strength, or a `PatternIndicator` for chart patterns)._
