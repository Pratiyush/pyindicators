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
        "derivative_osc", "rsl", "td_seq", "er", "slope", "pvo", "ttm_squeeze", "ttm_momentum",
        "disparity_index", "cmb_composite_index", "rsi_positive_reversal", "rsi_negative_reversal",
    ],
    "volatility": [
        "bbands", "atr", "natr", "keltner", "donchian", "cvi", "ulcer", "hv", "massi", "rvi",
        "accbands", "aberration", "chandelier", "hwc", "pdist", "thermo", "apz", "starc", "gsv",
    ],
    "volume": [
        "obv", "ad", "cmf", "adosc", "mfi", "vwap", "vp", "efi", "eom", "nvi", "pvi", "kvo",
        "vwmacd", "pvt", "vfi", "marketfi", "pvol", "pvr", "wad", "aobv", "rvol", "vol_sma", "fve",
        "vpa_climactic_bars", "vpa_no_supply", "vpa_no_demand", "vpa_stopping_volume",
        "vpa_effort_vs_result",
    ],
    "statistics": [
        "linreg", "linreg_slope", "linreg_intercept", "linreg_angle", "tsf", "correl", "beta",
        "zscore", "mad", "median", "quantile", "skew", "kurtosis", "entropy", "stderr",
        "r_squared", "covariance", "tos_stdevall", "hurst_exponent",
    ],
    "relative": ["rs_line", "mansfield_rs", "rs_rating"],
    "structure": [
        "rolling_high", "rolling_low", "pct_from_high", "pct_from_low",
        "renko", "kagi", "three_line_break",
    ],
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
        "spring", "upthrust", "big_shadow", "kangaroo_tail", "wammie", "moolah",
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


def _scan(predicate_dir: str) -> str:
    parts = []
    for path in (ROOT / "tests").rglob("*.py"):
        is_parity = "parity" in path.name
        if (predicate_dir == "parity") == is_parity:
            parts.append(path.read_text())
    return "\n".join(parts)


def _mentions(name: str, text: str) -> bool:
    return f'"{name}"' in text or f"'{name}'" in text


def build() -> str:
    registered = set(pyi.INDICATORS.names())
    golden_text = _scan("golden")
    parity_text = _scan("parity")

    total = sum(len(v) for v in TARGETS.values())
    done = sum(1 for ids in TARGETS.values() for n in ids if n in registered)
    lines = [
        "# pyindicators — build tracking dashboard",
        "",
        f"_Auto-generated by `scripts/build_tracking.py`._  "
        f"**{done} / {total} implemented ({100 * done // total}%).**",
        "",
        "Legend: ✅ yes · ⬜ no/pending. **Status** = Done (implemented + golden + parity) · "
        "🚧 In progress (implemented, missing a test) · ⬜ Pending (not built).",
        "",
    ]
    for category, ids in TARGETS.items():
        cat_done = sum(1 for n in ids if n in registered)
        lines.append(f"## {category} ({cat_done}/{len(ids)})")
        lines.append("")
        lines.append("| id | implemented | golden test | parity test | status |")
        lines.append("|----|-------------|-------------|-------------|--------|")
        for name in ids:
            impl = name in registered
            golden = _mentions(name, golden_text)
            parity = _mentions(name, parity_text)
            if not impl:
                status = "⬜ Pending"
            elif golden and parity:
                status = "✅ Done"
            else:
                status = "🚧 In progress"
            lines.append(
                f"| `{name}` | {'✅' if impl else '⬜'} | {'✅' if golden else '⬜'} "
                f"| {'✅' if parity else '⬜'} | {status} |"
            )
        lines.append("")

    lines.append("## Out of scope (deliberately excluded)")
    lines.append("")
    lines.append("Not per-symbol OHLCV indicators — these belong in the app/screener, not here.")
    lines.append("")
    for item, reason in OUT_OF_SCOPE.items():
        lines.append(f"- **{item}** — {reason}")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    (ROOT / "docs" / "TRACKING.md").write_text(build())
    print("wrote docs/TRACKING.md")
