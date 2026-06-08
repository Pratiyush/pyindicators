"""Per-indicator review pipeline — a repeatable, standing audit over the WHOLE registry.

Runs three review stages for every registered indicator and prints a per-indicator verdict,
so the one-off correctness audit becomes a command you can re-run any time:

    uv run python scripts/audit_indicators.py            # full table
    uv run python scripts/audit_indicators.py --fails    # only problems
    uv run python scripts/audit_indicators.py rsi macd   # specific indicators
    uv run python scripts/audit_indicators.py --write-md # regenerate docs/AUDIT.md from results

Review stages (the "3 types of review"):
  1. ROBUSTNESS / EDGE  — runs on constant, interior-NaN, 2-row and zero-volume frames; the
     output must keep the input length, never raise, never produce +/-inf, and respect the
     indicator's declared bounds on real data.
  2. CAUSALITY          — no look-ahead (compute(df[:k]) == compute(df)[:k]), deterministic
     (two runs identical), and no mutation of the input frame.
  3. PARITY COVERAGE    — confirms the indicator is cross-checked somewhere in tests/parity/
     and, when available, on real market data (tests using real_frame). Live numeric parity
     against the reference libraries lives in the pytest parity suite; this stage reports the
     coverage so gaps are visible.

Exit code is non-zero if any indicator fails stage 1 or 2 (hard correctness), making it safe to
wire into a build/lint step. Stage-3 gaps are reported as warnings, not failures.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

import pyindicators as pyi

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "tests" / "data" / "aapl_daily.csv"
OHLCV = ("open", "high", "low", "close", "volume")


def _real() -> pd.DataFrame:
    return pd.read_csv(DATA)[list(OHLCV)].reset_index(drop=True)


def _const(n: int = 60) -> pd.DataFrame:
    v = np.full(n, 50.0)
    return pd.DataFrame({"open": v, "high": v, "low": v, "close": v, "volume": v})


def _nan_tick(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.loc[out.index[10], "close"] = np.nan
    return out


def _zero_vol(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["volume"] = 0.0
    return out


def _parity_corpus() -> tuple[str, str]:
    parity, real = [], []
    for path in (ROOT / "tests" / "parity").rglob("*.py"):
        text = path.read_text()
        parity.append(text)
        if "real_frame" in text:
            real.append(text)
    return "\n".join(parity), "\n".join(real)


def _mentioned(name: str, text: str) -> bool:
    return f'"{name}"' in text or f"'{name}'" in text


def review_robustness(ind, real: pd.DataFrame) -> list[str]:
    """Stage 1: edge frames never crash; output well-formed; declared bounds hold."""
    problems = []
    frames = {
        "real": real,
        "constant": _const(),
        "nan_tick": _nan_tick(real),
        "two_row": real.iloc[:2].copy(),
        "zero_volume": _zero_vol(real),
    }
    for label, df in frames.items():
        try:
            out = ind.compute(df)
        except Exception as exc:  # noqa: BLE001 - we want to report ANY crash
            problems.append(f"crash on {label}: {type(exc).__name__}: {exc}")
            continue
        if len(out) != len(df):
            problems.append(f"length changed on {label} ({len(out)} != {len(df)})")
        if np.isinf(out.to_numpy(dtype="float64")).any():
            problems.append(f"infinity in output on {label}")
    out_real = ind.compute(real)
    for col, (lo, hi) in (ind.spec.bounds or {}).items():
        vals = out_real[col].to_numpy(dtype="float64")
        finite = vals[np.isfinite(vals)]
        if finite.size and (finite.min() < lo - 1e-9 or finite.max() > hi + 1e-9):
            problems.append(f"bound breach {col} [{finite.min():.4g},{finite.max():.4g}] !in [{lo},{hi}]")
    return problems


def review_causality(ind, real: pd.DataFrame) -> list[str]:
    """Stage 2: no look-ahead, deterministic, no input mutation."""
    problems = []
    before = real.copy(deep=True)
    full = ind.compute(real)
    again = ind.compute(real)
    if not full.equals(again):
        problems.append("non-deterministic (two computes differ)")
    if not real.equals(before):
        problems.append("mutated the input frame")
    if ind.spec.causal:
        for k in (30, len(real) // 2, len(real) - 1):
            trunc = ind.compute(real.iloc[:k].copy())
            a = full.iloc[:k].to_numpy(dtype="float64")
            b = trunc.to_numpy(dtype="float64")
            mask = np.isfinite(a) & np.isfinite(b)
            if mask.size and not np.allclose(a[mask], b[mask], rtol=1e-9, atol=1e-9):
                problems.append(f"look-ahead: prefix[:{k}] != truncated compute")
                break
    return problems


def review_parity_coverage(name: str, parity_text: str, real_text: str) -> list[str]:
    """Stage 3 (warnings): is the indicator cross-checked, and on real data?"""
    warns = []
    if not _mentioned(name, parity_text):
        warns.append("no parity test")
    if not _mentioned(name, real_text):
        warns.append("no real-data test")
    return warns


def audit_records(names: list[str] | None = None) -> list[dict]:
    """Run all three stages over ``names`` (default: whole registry) and return structured
    records — the single source of truth consumed by the console report, ``docs/AUDIT.md``, and
    the tracker's ``review`` column. Each record: name, category, verdict (ok/warn/FAIL), the
    hard problems (stages 1-2), and the coverage warnings (stage 3)."""
    real = _real()
    parity_text, real_text = _parity_corpus()
    records = []
    for name in names or pyi.INDICATORS.names():
        ind = pyi.INDICATORS.create(name)
        hard = review_robustness(ind, real) + review_causality(ind, real)
        warns = review_parity_coverage(name, parity_text, real_text)
        verdict = "FAIL" if hard else ("warn" if warns else "ok")
        records.append(
            {
                "name": name,
                "category": ind.spec.category,
                "verdict": verdict,
                "problems": hard,
                "coverage": warns,
            }
        )
    return records


#: Indicators that have ALSO had an individual line-by-line correctness + test-case code review
#: written up (beyond the automated stages). See ref/AUDIT_*.md. The automated audit is the
#: source of truth for pass/fail; this set records where the deep-dive prose exists.
DEEP_REVIEWED: set[str] = {
    "sma", "ema", "wma", "rma", "stdev", "variance", "true_range",
    "hl2", "hlc3", "ohlc4", "wcp", "midpoint", "midprice", "heikin_ashi",
    "linreg", "linreg_slope", "linreg_intercept", "linreg_angle", "tsf", "zscore", "mad",
    "median", "quantile", "skew", "kurtosis", "entropy", "hurst_exponent",
    "rs_rating", "rolling_high", "rolling_low", "pct_from_high", "pct_from_low",
    # math_transform (ref/AUDIT_math_transform.md)
    "acos", "asin", "atan", "cos", "cosh", "sin", "sinh", "tan", "tanh", "exp", "ln", "log10",
    "sqrt", "ceil", "floor", "add", "sub", "mult", "div", "max", "min", "sum", "minmax",
    "maxindex", "minindex", "minmaxindex",
    # candles (ref/AUDIT_candles.md) — 61 exact-parity vs talib.CDL* + 4 VSA extras
    "two_crows", "three_black_crows", "three_inside", "three_line_strike", "three_outside",
    "three_stars_in_south", "three_white_soldiers", "abandoned_baby", "advance_block",
    "belt_hold", "breakaway", "closing_marubozu", "conceal_baby_swallow", "counterattack",
    "dark_cloud_cover", "doji", "doji_star", "dragonfly_doji", "engulfing", "evening_doji_star",
    "evening_star", "gap_side_side_white", "gravestone_doji", "hammer", "hanging_man", "harami",
    "harami_cross", "high_wave", "hikkake", "hikkake_mod", "homing_pigeon", "identical_three_crows",
    "in_neck", "inverted_hammer", "kicking", "kicking_by_length", "ladder_bottom",
    "long_legged_doji", "long_line", "marubozu", "matching_low", "mat_hold", "morning_doji_star",
    "morning_star", "on_neck", "piercing", "rickshaw_man", "rise_fall_three_methods",
    "separating_lines", "shooting_star", "short_line", "spinning_top", "stalled_pattern",
    "stick_sandwich", "takuri", "tasuki_gap", "thrusting", "tristar", "unique_three_river",
    "upside_gap_two_crows", "xside_gap_three_methods", "spring", "upthrust", "big_shadow",
    "kangaroo_tail",
    # utils + statistics extras + cycle (ref/AUDIT_utils_stats_cycle.md)
    "crossover", "crossunder", "crossany", "cross_value", "lag", "decay", "edecay",
    "percent_rank", "roc1",
    "correl", "beta", "covariance", "r_squared", "stderr", "tos_stdevall",
    "ht_dcperiod", "ht_dcphase", "ht_phasor", "ht_sine", "ht_trendmode", "ht_trendline",
    "ebsw", "dsp", "msw",
    # volatility + volume (ref/AUDIT_volatility_volume.md)
    "bbands", "atr", "natr", "keltner", "donchian", "cvi", "ulcer", "hv", "massi", "rvi",
    "accbands", "aberration", "chandelier", "hwc", "pdist", "thermo", "apz", "starc",
    "obv", "ad", "cmf", "adosc", "mfi", "vwap", "efi", "eom", "nvi", "pvi", "kvo", "vwmacd",
    "pvt", "vfi", "marketfi", "pvol", "pvr", "wad", "aobv", "rvol", "vol_sma", "fve",
    "vpa_climactic_bars", "vpa_no_supply", "vpa_no_demand", "vpa_stopping_volume",
    "vpa_effort_vs_result",
    # trend (ref/AUDIT_trend.md)
    "dema", "tema", "trima", "kama", "hma", "vwma", "alma", "zlma", "t3", "frama", "vidya",
    "fwma", "sinwma", "swma", "pwma", "hwma", "jma", "mcgd", "mama", "fama", "ssf", "vama",
    "evwma", "lsma", "hilo", "rainbow", "sma_slope", "ma_spread", "macd", "macdext", "macdfix",
    "ppo", "apo", "adx", "adxr", "dx", "plus_di", "minus_di", "plus_dm", "minus_dm", "aroon",
    "aroon_osc", "psar", "sarext", "supertrend", "ichimoku", "vortex", "trix", "kst", "dpo",
    "chop", "vhf", "cksp", "qstick", "ttm_trend", "increasing", "decreasing", "amat", "pmax",
    "pivots", "long_run", "short_run",
}

# The 7 convention/scale concerns surfaced by the original four-way manual audit — all resolved.
# Kept as narrative (the automated stages verify correctness, not citation conventions).
_RESOLVED_CONCERNS = [
    ("bb_bandwidth", "ours `(U-L)/M`; pandas-ta/StockCharts/TradingView use `×100`",
     "**aligned to ×100** (behaviour + golden test)"),
    ("cmo", "claimed TA-Lib CMO but matched pandas-ta's simple-sum CMO (TA-Lib uses Wilder)",
     "`talib_compatible=False`, references/docstring corrected"),
    ("trix (signal)", "line matches TA-Lib/pandas-ta; signal is EMA(9) vs pandas-ta SMA(9)",
     "docstring states the signal convention"),
    ("kst", "matches StockCharts/`ta`; pandas-ta is 100× (non-standard)",
     "docstring notes it; parity test ÷100"),
    ("pvt", "canonical StockCharts fractional form; pandas-ta is 100×",
     "docstring notes it; parity test ÷100"),
    ("pvr", "bar 0 NaN (no prior); pandas-ta fills 0 → rank 1 there",
     "docstring notes it; all later bars match"),
    ("alma", "deliberately matches TradingView/Pine; pandas-ta reverses the weights",
     "already documented (no change)"),
]


def generate_audit_md(records: list[dict]) -> str:
    """Render ``docs/AUDIT.md`` from live audit records — counts are computed, never hardcoded."""
    total = len(records)
    n_ok = sum(1 for r in records if r["verdict"] == "ok")
    n_warn = sum(1 for r in records if r["verdict"] == "warn")
    n_fail = sum(1 for r in records if r["verdict"] == "FAIL")

    # group by category for the per-stage breakdown
    cats: dict[str, list[dict]] = {}
    for r in records:
        cats.setdefault(r["category"], []).append(r)

    lines = [
        "# pyindicators — correctness audit",
        "",
        "_Auto-generated by `scripts/audit_indicators.py --write-md` — do not edit by hand._",
        "",
        "Every registered indicator is run through three review stages (defined in "
        "`scripts/audit_indicators.py`) on real AAPL daily data plus constant / interior-NaN / "
        "2-row / zero-volume edge frames. Re-run any time:",
        "",
        "    uv run python scripts/audit_indicators.py              # console table",
        "    uv run python scripts/audit_indicators.py --write-md   # regenerate this file",
        "",
        "1. **Robustness / edge** — no crash, length preserved, no ±inf, declared bounds hold.",
        "2. **Causality** — no look-ahead (`compute(df[:k]) == compute(df)[:k]`), deterministic, "
        "no input mutation.",
        "3. **Parity coverage** — has a parity test and a real-data test (a coverage warning, not "
        "a correctness failure).",
        "",
        f"## Result: **{n_fail} correctness failures** across {total} indicators",
        "",
        f"- ✅ fully clean (passes all three stages): **{n_ok}**",
        f"- ⚠️ correct but missing parity/real-data coverage (stage 3): **{n_warn}**",
        f"- ❌ hard correctness failure (stage 1 or 2): **{n_fail}**",
        "",
        "| category | indicators | clean | coverage-warn | FAIL |",
        "|----------|-----------:|------:|--------------:|-----:|",
    ]
    for cat in sorted(cats):
        rs = cats[cat]
        c_ok = sum(1 for r in rs if r["verdict"] == "ok")
        c_warn = sum(1 for r in rs if r["verdict"] == "warn")
        c_fail = sum(1 for r in rs if r["verdict"] == "FAIL")
        lines.append(f"| {cat} | {len(rs)} | {c_ok} | {c_warn} | {c_fail} |")
    lines += [f"| **total** | **{total}** | **{n_ok}** | **{n_warn}** | **{n_fail}** |", ""]

    if n_fail:
        lines += ["## ❌ Correctness failures", "",
                  "| indicator | problem |", "|-----------|---------|"]
        for r in records:
            if r["verdict"] == "FAIL":
                lines.append(f"| `{r['name']}` | {'; '.join(r['problems'])} |")
        lines.append("")

    lines += [
        "## Convention/scale concerns from the original manual audit — all resolved",
        "",
        "These were places our output equalled a defensible canonical definition but diverged "
        "from a *cited* reference by a constant factor or smoother choice — resolved by aligning "
        "to the standard where one exists, else documenting the convention.",
        "",
        "| indicator | finding | resolution |",
        "|-----------|---------|------------|",
    ]
    for ind, finding, res in _RESOLVED_CONCERNS:
        lines.append(f"| `{ind}` | {finding} | {res} |")

    n_deep = sum(1 for r in records if r["name"] in DEEP_REVIEWED)
    lines += [
        "",
        "## Individual code reviews",
        "",
        f"**{n_deep}** indicators additionally have a line-by-line implementation + test-case "
        "code review: see `ref/AUDIT_base_pricetransform_stats_relative_structure.md` "
        "(base / price_transform / statistics / relative / structure).",
        "",
        "Per-indicator build + audit status (including the coverage-warn backfill list) lives in "
        "the single source-of-truth dashboard `docs/TRACKING.md`.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if "--write-md" in argv:
        records = audit_records()
        (ROOT / "docs" / "AUDIT.md").write_text(generate_audit_md(records))
        n_fail = sum(1 for r in records if r["verdict"] == "FAIL")
        print(f"wrote docs/AUDIT.md ({len(records)} indicators, {n_fail} FAIL)")
        return 1 if n_fail else 0

    only_fails = "--fails" in argv
    requested = [a for a in argv if not a.startswith("--")]
    names = requested or pyi.INDICATORS.names()
    records = audit_records(names)

    rows = [r for r in records if not (only_fails and r["verdict"] == "ok")]
    width = max((len(r["name"]) for r in rows), default=4)
    for r in rows:
        mark = {"ok": "OK  ", "warn": "WARN", "FAIL": "FAIL"}[r["verdict"]]
        notes = "; ".join(r["problems"] + [f"(coverage) {w}" for w in r["coverage"]])
        print(f"{mark}  {r['name']:<{width}}  {notes}")
    hard_fail = sum(1 for r in records if r["verdict"] == "FAIL")
    warn_only = sum(1 for r in records if r["verdict"] == "warn")
    print(
        f"\n{len(names)} indicators reviewed — "
        f"{len(names) - hard_fail - warn_only} ok, {warn_only} coverage-warn, {hard_fail} FAIL"
    )
    return 1 if hard_fail else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
