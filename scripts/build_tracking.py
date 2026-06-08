"""Regenerate ``docs/TRACKING.md`` — the master build dashboard.

Lists the FULL target catalog (every indicator we intend to ship, whether built yet or not)
and each one's pipeline status, derived from:
- the live registry (implemented?),
- a scan of the test suite (has a golden test? a parity test?),
- the reference specs under ``ref/ta_docs``.

Run:  uv run python scripts/build_tracking.py

This is a dev tool (not shipped, not part of coverage). The TARGETS dict below is the
hand-maintained source of truth for "what should exist"; add to it as scope grows.
OUT_OF_SCOPE records what we deliberately exclude (and why) so it's never re-litigated.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pyindicators as pyi  # noqa: E402
from pyindicators.catalog import catalog_rows  # noqa: E402

# Reuse the audit pipeline as the single source for review status (so the tracker, docs/AUDIT.md
# and the audit command never disagree). DEEP_REVIEWED = indicators with a line-by-line code
# review writeup; audit_records() = the live 3-stage verdict per indicator.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_indicators import DEEP_REVIEWED, audit_records  # noqa: E402

# Per-indicator metadata (outputs/inputs/aliases) keyed by name. `import pyindicators` above has
# already registered every indicator, so this captures the full built set. Same source that
# rendered the retired docs/CATALOG.md — keeps the tracker in lock-step with the registry.
_META: dict[str, dict] = {row["name"]: row for row in catalog_rows()}

# Full target catalog (deduped: each id appears under one primary category).
TARGETS: dict[str, list[str]] = {
    "base": ["sma", "ema", "wma", "rma", "stdev", "variance", "true_range"],
    "price_transform": ["hl2", "hlc3", "ohlc4", "wcp", "midpoint", "midprice", "heikin_ashi"],
    "trend": [
        # moving averages
        "dema", "tema", "trima", "kama", "hma", "vwma", "alma", "zlma", "t3", "frama", "vidya",
        "fwma", "sinwma", "swma", "pwma", "hwma", "jma", "mcgd", "mama", "fama", "ssf", "vama",
        "evwma", "lsma", "hilo", "rainbow", "sma_slope", "ma_spread",
        # directional / trend systems
        "macd", "macdext", "macdfix", "ppo", "apo", "adx", "adxr", "dx", "plus_di", "minus_di",
        "plus_dm", "minus_dm", "aroon", "aroon_osc", "psar", "sarext", "supertrend", "ichimoku",
        "vortex", "trix", "kst", "dpo", "chop", "vhf", "cksp", "qstick", "stc", "ttm_trend",
        "increasing", "decreasing", "amat", "pmax", "pivots", "long_run", "short_run",
    ],
    "momentum": [
        "rsi", "stoch", "stochf", "stochrsi", "willr", "cci", "roc", "rocp", "rocr", "rocr100",
        "mom", "tsi", "uo", "ao", "cmo", "fisher", "crsi", "rvgi", "coppock", "bop", "kdj", "smi",
        "eri", "inertia", "bias", "brar", "cg", "cfo", "fosc", "pgo", "psl", "qqe", "rsx", "cti",
        "squeeze", "squeeze_pro", "alligator", "gator", "laguerre_rsi", "demarker",
        "derivative_osc", "rsl", "td_seq", "er", "slope", "pvo", "ttm_momentum",
        "disparity_index", "cmb_composite_index", "rsi_positive_reversal", "rsi_negative_reversal",
    ],
    "volatility": [
        "bbands", "atr", "natr", "keltner", "donchian", "cvi", "ulcer", "hv", "massi", "rvi",
        "accbands", "aberration", "chandelier", "hwc", "pdist", "thermo", "apz", "starc",
    ],
    "volume": [
        "obv", "ad", "cmf", "adosc", "mfi", "vwap", "efi", "eom", "nvi", "pvi", "kvo",
        "vwmacd", "pvt", "vfi", "marketfi", "pvol", "pvr", "wad", "aobv", "rvol", "vol_sma", "fve",
        "vpa_climactic_bars", "vpa_no_supply", "vpa_no_demand", "vpa_stopping_volume",
        "vpa_effort_vs_result",
    ],
    "statistics": [
        "linreg", "linreg_slope", "linreg_intercept", "linreg_angle", "tsf", "correl", "beta",
        "zscore", "mad", "median", "quantile", "skew", "kurtosis", "entropy", "stderr",
        "r_squared", "covariance", "tos_stdevall", "hurst_exponent",
    ],
    "relative": ["rs_rating"],
    "structure": ["rolling_high", "rolling_low", "pct_from_high", "pct_from_low"],
    "cycle": [
        "ht_dcperiod", "ht_dcphase", "ht_phasor", "ht_sine", "ht_trendmode", "ht_trendline",
        "ebsw", "dsp", "msw",
    ],
    "math_transform": [
        "acos", "asin", "atan", "cos", "cosh", "sin", "sinh", "tan", "tanh", "ceil", "floor",
        "exp", "ln", "log10", "sqrt", "min", "max", "minindex", "maxindex", "minmax",
        "minmaxindex", "sum", "add", "sub", "mult", "div",
    ],
    "utils": [
        "crossover", "crossunder", "crossany", "cross_value", "lag", "decay", "edecay",
        "percent_rank", "roc1",
    ],
    "candles": [
        "two_crows", "three_black_crows", "three_inside", "three_line_strike", "three_outside",
        "three_stars_in_south", "three_white_soldiers", "abandoned_baby", "advance_block",
        "belt_hold", "breakaway", "closing_marubozu", "conceal_baby_swallow", "counterattack",
        "dark_cloud_cover", "doji", "doji_star", "dragonfly_doji", "engulfing",
        "evening_doji_star", "evening_star", "gap_side_side_white", "gravestone_doji", "hammer",
        "hanging_man", "harami", "harami_cross", "high_wave", "hikkake", "hikkake_mod",
        "homing_pigeon", "identical_three_crows", "in_neck", "inverted_hammer", "kicking",
        "kicking_by_length", "ladder_bottom", "long_legged_doji", "long_line", "marubozu",
        "matching_low", "mat_hold", "morning_doji_star", "morning_star", "on_neck", "piercing",
        "rickshaw_man", "rise_fall_three_methods", "separating_lines", "shooting_star",
        "short_line", "spinning_top", "stalled_pattern", "stick_sandwich", "takuri", "tasuki_gap",
        "thrusting", "tristar", "unique_three_river", "upside_gap_two_crows",
        "xside_gap_three_methods",
        # VSA / price-action extras beyond the 61 TA-Lib CDL set
        "spring", "upthrust", "big_shadow", "kangaroo_tail",
    ],
}

# Deliberately excluded (not a per-symbol OHLCV indicator) — recorded so it's not re-litigated.
OUT_OF_SCOPE: dict[str, str] = {
    "market breadth (McClellan, AD line, TRIN, diffusion)": "needs the whole universe's adv/decl",
    "fundamentals (P/E, PEG, ROE, EPS growth, FCF, CAPE)": "not derivable from OHLCV",
    "sentiment (VIX, put/call, COT, news)": "external non-price data",
    "subjective chart patterns (head&shoulders, triangles, flags, cup&handle)": "need pivot fitting",
    "harmonic & Elliott (Gartley, Butterfly, Bat, Crab, waves)": "subjective Fibonacci/wave fitting",
    "pairs / cointegration / Kalman hedge": "two-symbol statistical arbitrage",
    "supply/demand zones, order blocks, trendline-with-authority": "subjective zone/line detection",
}

# Real future indicators that need a DIFFERENT contract than the per-bar, single-symbol, 1:1
# ``Indicator`` base (a benchmark series, bar-resampling, or volume-by-price binning) — or that
# have no defensible spec. Deferred by design, NOT "in-scope but unbuilt". See docs/BACKLOG.md.
DEFERRED: dict[str, str] = {
    "ttm_squeeze": "alias of `squeeze` (TTM Squeeze *is* the built `squeeze`) — documented, no 2nd impl",
    "rs_line": "needs a benchmark/index series → 2-input relative-strength contract (app/screener)",
    "mansfield_rs": "needs a benchmark/index series → 2-input relative-strength contract (app/screener)",
    "renko": "rebins bars; output not 1:1 with the input index → chart-transform sub-module",
    "kagi": "rebins bars; output not 1:1 with the input index → chart-transform sub-module",
    "three_line_break": "rebins bars; output not 1:1 with the input index → chart-transform sub-module",
    "vp": "volume-by-price histogram (not a per-bar series) → sub-module",
    "gsv": "no defensible definition/oracle in any reference lib — research the spec before building",
    "wammie": "no authoritative definition or oracle in any reference lib — dropped unless a spec surfaces",
    "moolah": "no authoritative definition or oracle in any reference lib — dropped unless a spec surfaces",
}


def _scan(predicate_dir: str) -> str:
    parts = []
    for path in (ROOT / "tests").rglob("*.py"):
        # Classify by directory, not a substring of the filename: ``test_disparity.py`` is a
        # golden unit test, not a parity test, even though "disparity" contains "parity".
        is_parity = "parity" in path.parts
        if (predicate_dir == "parity") == is_parity:
            parts.append(path.read_text())
    return "\n".join(parts)


def _mentions(name: str, text: str) -> bool:
    return f'"{name}"' in text or f"'{name}'" in text


def _m(flag: bool) -> str:
    return "✅" if flag else "⬜"


def _meta(name: str) -> tuple[str, str, str]:
    """(outputs, inputs, aliases) for an indicator; ``—`` for each if it isn't built yet.

    Sources from :func:`pyindicators.catalog.catalog_rows` — the same registry-derived metadata
    that used to render the now-retired docs/CATALOG.md — so TRACKING.md is the single source of
    truth (per-indicator metadata + build/quality status) and can never drift from the code.
    """
    row = _META.get(name)
    if row is None:
        return "—", "—", "—"
    outputs = ", ".join(row["outputs"])
    inputs = ", ".join(row["inputs"])
    aliases = ", ".join(row["aliases"]) if row["aliases"] else "—"
    return outputs, inputs, aliases


def _scan_files_with(token: str) -> str:
    """Concatenate every test file that references ``token`` (e.g. ``real_frame``)."""
    parts = []
    for path in (ROOT / "tests").rglob("*.py"):
        text = path.read_text()
        if token in text:
            parts.append(text)
    return "\n".join(parts)


def build() -> str:
    registered = set(pyi.INDICATORS.names())
    # utils ships some members as plain functions (crossover family) rather than registered
    # Indicators — count those as implemented too (they have no registry spec).
    registered |= {
        n for n in dir(pyi.utils)
        if not n.startswith("_") and callable(getattr(pyi.utils, n)) and not isinstance(getattr(pyi.utils, n), type)
    }
    golden_text = _scan("golden")
    parity_text = _scan("parity")
    real_text = _scan_files_with("real_frame")  # tests exercising genuine market data
    xlib_text = (ROOT / "tests" / "parity" / "test_real_multi.py").read_text()  # >=3-lib module
    audit = {r["name"]: r["verdict"] for r in audit_records()}  # live 3-stage audit verdict

    total = sum(len(v) for v in TARGETS.values())
    done = sum(1 for ids in TARGETS.values() for n in ids if n in registered)
    n_clean = sum(1 for v in audit.values() if v == "ok")
    n_fail = sum(1 for v in audit.values() if v == "FAIL")
    lines = [
        "# pyindicators — build tracking dashboard",
        "",
        f"_Auto-generated by `scripts/build_tracking.py`._  "
        f"**{done} / {total} implemented ({100 * done // total}%).**  "
        f"Audit (`scripts/audit_indicators.py`): **{n_fail} correctness failures** across "
        f"{len(audit)} built indicators · {n_clean} fully clean · "
        f"{len(DEEP_REVIEWED)} with a line-by-line code review.",
        "",
        "This is the single source of truth for the indicator set: per-indicator metadata "
        "(**outputs / inputs / aliases**, from the live registry) plus build, quality and audit "
        "status. Not-yet-built indicators show `—` for metadata. Full audit writeup: "
        "`docs/AUDIT.md`.",
        "",
        "Legend: ✅ yes · ⬜ no/pending. **Status** = Done (implemented + edge + parity) · "
        "🚧 In progress (implemented, missing a test) · ⬜ Pending (not built). The "
        "**3-lib / real / invalid** columns track the quality bar below — built indicators that "
        "predate a rule are backfilled incrementally (⬜ = todo, not a regression). **audit** = "
        "the live 3-stage audit verdict (✅ clean · ⚠️ correct but missing parity/real coverage · "
        "❌ correctness failure · — not built). **review** = has a line-by-line implementation + "
        "test-case code review (`ref/AUDIT_base_pricetransform_stats_relative_structure.md`).",
        "",
        "## Definition of Done (per indicator) — the quality checklist",
        "",
        "1. One file, typed metadata + params, composes `base/` (never re-inlines).",
        "2. **Separate test file(s)** under `tests/<category>/` (golden) and `tests/parity/`.",
        "3. **Edge cases**: flat/constant, warm-up boundary, short frames, zero-range/zero-vol.",
        "4. **Invalid-value testing**: bad params rejected, missing columns raise, NaN tolerated "
        "— guaranteed for every indicator by `tests/meta/test_invalid_inputs.py` (registry-driven).",
        "5. **Parity vs >= 3 independent libraries** where they ship it (TA-Lib, pandas-ta, "
        "finta, bukosabino-`ta`) — known variants excluded with a comment, never silently. "
        "Advanced indicators that exist in only one reference lib are validated against that one.",
        "6. **Real-data parity** on `tests/data/aapl_daily.csv` via `ohlcv_gen.real_frame()`, "
        "not only the synthetic walk.",
        "7. **100% line+branch coverage** (enforced globally) + registry meta-tests + ruff clean.",
        "8. docs/TRACKING.md regenerated (the single source of truth — metadata + status); "
        "committed (authored by Pratiyush).",
        "",
        "**Guideline:** as each indicator is completed, tick its row below; when a new rule is "
        "added, backfill the column for prebuilt indicators over time. Synthetic-only data hides "
        "tie/seed bugs (e.g. it missed the Aroon tie bug) — real data and multiple libraries are "
        "what catch them.",
        "",
        "**Review pipeline:** `uv run python scripts/audit_indicators.py` re-runs the three "
        "review stages (robustness/edge+bounds, causality/determinism, parity coverage) over the "
        "whole registry and exits non-zero on any hard failure — a repeatable standing audit.",
        "",
    ]
    for category, ids in TARGETS.items():
        cat_done = sum(1 for n in ids if n in registered)
        lines.append(f"## {category} ({cat_done}/{len(ids)})")
        lines.append("")
        lines.append(
            "| id | outputs | inputs | aliases | impl | edge | parity | 3-lib | real "
            "| invalid | audit | review | status |"
        )
        lines.append(
            "|----|---------|--------|---------|------|------|--------|-------|------"
            "|---------|-------|--------|--------|"
        )
        for name in ids:
            impl = name in registered
            outputs, inputs, aliases = _meta(name)
            golden = _mentions(name, golden_text)
            parity = _mentions(name, parity_text)
            xlib = _mentions(name, xlib_text)  # cross-checked vs >=3 libs (test_real_multi)
            real = _mentions(name, real_text)  # has a real-data test
            invalid = impl  # every registered indicator is covered by the invalid-input meta-test
            audit_mark = {"ok": "✅", "warn": "⚠️", "FAIL": "❌"}.get(audit.get(name), "—")
            review = name in DEEP_REVIEWED  # has a line-by-line code review (ref/AUDIT_*.md)
            if not impl:
                status = "⬜ Pending"
            elif golden and parity:
                status = "✅ Done"
            else:
                status = "🚧 In progress"
            lines.append(
                f"| `{name}` | {outputs} | {inputs} | {aliases} | {_m(impl)} | {_m(golden)} "
                f"| {_m(parity)} | {_m(xlib)} | {_m(real)} | {_m(invalid)} | {audit_mark} "
                f"| {_m(review)} "
                f"| {status} |"
            )
        lines.append("")

    lines.append("## Out of scope (deliberately excluded)")
    lines.append("")
    lines.append("Not per-symbol OHLCV indicators — these belong in the app/screener, not here.")
    lines.append("")
    for item, reason in OUT_OF_SCOPE.items():
        lines.append(f"- **{item}** — {reason}")
    lines.append("")

    lines.append("## Deferred (needs a different contract than the per-bar `Indicator`)")
    lines.append("")
    lines.append(
        f"{len(DEFERRED)} items from the research catalog are **not** plain per-symbol 1:1 OHLCV "
        "indicators, so they don't fit this library's core contract today (they need a benchmark "
        "series, bar-resampling, volume-by-price binning, or a defensible spec). Recorded here so "
        "they read as *deferred by design*, not as missing work. Full plan: `docs/BACKLOG.md`."
    )
    lines.append("")
    for item, reason in DEFERRED.items():
        lines.append(f"- **`{item}`** — {reason}")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    (ROOT / "docs" / "TRACKING.md").write_text(build())
    print("wrote docs/TRACKING.md")
