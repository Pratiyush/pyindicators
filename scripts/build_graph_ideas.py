"""Generate one Markdown file of *visualization ideas* per indicator (docs/graphs/<name>.md).

These are charting ideas only (no plotting code): where to draw the indicator (price overlay vs
a separate pane), what scale / reference lines to use, how to render each output, and which
visual signals to highlight. Everything is derived from the registry ``IndicatorSpec`` (category,
inputs, outputs, bounds, flags) + the indicator docstring, so it can never drift from the code.

    uv run python scripts/build_graph_ideas.py        # writes docs/graphs/*.md + docs/graphs/README.md
"""

from __future__ import annotations

from pathlib import Path

import pyindicators as pyi
from pyindicators.core import CATEGORIES

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "graphs"

# Trend indicators that belong in a *separate pane* (oscillators), not as a price overlay.
TREND_PANE = {
    "macd", "macdext", "macdfix", "ppo", "apo", "trix", "kst", "dpo", "chop", "vhf",
    "aroon", "aroon_osc", "adx", "adxr", "dx", "plus_di", "minus_di", "plus_dm", "minus_dm",
    "vortex", "qstick", "sma_slope", "ma_spread", "increasing", "decreasing", "long_run",
    "short_run", "amat",
}
# Non-trend indicators that are still price overlays (base MAs, regression lines, price levels).
PRICE_OVERLAY = {
    "rolling_high", "rolling_low", "ht_trendline", "vwap", "pivots",
    "sma", "ema", "wma", "rma",            # base moving averages
    "linreg", "tsf", "median", "quantile",  # regression / price-level statistics
}
# Math transforms that overlay (rolling reducers on price); the rest are pane/utility.
MATH_OVERLAY = {"max", "min", "sum", "minmax", "midpoint", "midprice"}


def _what(name: str) -> str:
    """First 'What:' line of the indicator docstring (falls back to the summary line)."""
    doc = (pyi.INDICATORS.get(name).__doc__ or "").strip()
    for line in doc.splitlines():
        s = line.strip()
        if s.lower().startswith("what:"):
            return s.split(":", 1)[1].strip()
    return doc.splitlines()[0].strip() if doc else ""


def classify(spec) -> str:
    o = spec.outputs
    nm, cat, bounds = spec.name, spec.category, spec.bounds
    has_band = any(any(k in c for k in ("upper", "lower", "_ub", "_lb", "band")) for c in o)
    if cat == "candles":
        return "markers"
    if has_band:
        return "band"
    if cat == "price_transform" or nm in PRICE_OVERLAY:
        return "overlay"
    if cat == "trend" and nm not in TREND_PANE:
        return "overlay"
    if cat == "math_transform":
        return "overlay" if nm in MATH_OVERLAY else "pane"
    if nm in ("supertrend", "psar", "sarext", "pmax", "cksp", "hilo", "alligator", "ichimoku"):
        return "overlay"
    if bounds:
        return "bounded_pane"
    return "pane"


def _levels(spec) -> str:
    if not spec.bounds:
        return ""
    lo, hi = next(iter(spec.bounds.values()))
    if (lo, hi) == (0.0, 100.0):
        return "0–100. Draw overbought/oversold guides at **70 / 30** (or 80 / 20) and a 50 midline."
    if (lo, hi) == (-100.0, 0.0):
        return "−100–0. Draw guides at **−20 / −80** (overbought / oversold)."
    if (lo, hi) == (0.0, 1.0):
        return "0–1 (a flag/probability). Treat ≥ 0.5 as 'on'."
    return f"bounded to [{lo:g}, {hi:g}]; draw guide lines near the extremes."


PLACEMENT = {
    "overlay": "**Overlay on the price chart** — same axes as candlesticks, sharing the time x-axis. "
    "Plot it as a line tracking price; it is directly comparable to the close.",
    "band": "**Overlay on the price chart as a channel/band** — draw the upper and lower lines and "
    "**shade the area between them**; plot the middle line dashed. Price riding the bands is the signal.",
    "bounded_pane": "**A separate pane below the price chart**, aligned on the same time axis. It is a "
    "bounded oscillator, so it gets its own fixed vertical scale.",
    "pane": "**A separate pane below the price chart**, aligned on the same time axis. Centre it on its "
    "zero/neutral line so positive vs negative is obvious at a glance.",
    "markers": "**Markers on the price chart** — place a symbol at each bar the pattern fires (no line). "
    "Use an up-triangle below the bar for a bullish print and a down-triangle above for a bearish one.",
}

SKETCH = {
    "overlay": "price + line overlay:\n\n    price ╱╲    ╱╲\n         ╱  ╲  ╱  ╲____   ← close (candles)\n    ────╱────╲╱────────   ← indicator line\n",
    "band": "price inside a shaded channel:\n\n    ┌───────────────┐ upper\n    │░░░╱╲░░░░╱╲░░░░░│  (shade between bands)\n    │░╱░░╲░░╱░░╲░░░░░│ ← price\n    └───────────────┘ lower\n",
    "bounded_pane": "lower pane, 0–100 with guides:\n\n    100 ┤\n     70 ┤╌╌╌╌╌╱╲╌╌╌╌╌  overbought\n        │   ╱  ╲\n     30 ┤╌╲╌╱╌╌╌╌╲╌╌╌  oversold\n      0 ┤\n",
    "pane": "lower pane, centred on zero:\n\n      + ┤    ╱╲\n      0 ┤───╱──╲────  zero line\n      − ┤  ╱    ╲╱\n",
    "markers": "markers on price:\n\n    price ╱╲   ▼      ← bearish print\n         ╱  ╲ ╱╲\n        ╱    ╲  ▲    ← bullish print\n",
}

SIGNALS = {
    "overlay": "- **Price/line crossovers** — close crossing above the line = bullish, below = bearish (shade or mark the cross).\n"
    "- **Slope** — colour the line green when rising, red when falling.\n"
    "- **Distance** — how far price has stretched from the line (mean-reversion hint).",
    "band": "- **Band touches / breaks** — closes outside a band flag stretch or breakout.\n"
    "- **Squeeze** — bands narrowing = low volatility, often before a move; shade the squeeze.\n"
    "- **Walking the band** — successive closes hugging one band = strong trend.",
    "bounded_pane": "- **Threshold breaches** — shade the region above/below the overbought/oversold guides.\n"
    "- **Guide crossings** — mark when it crosses back through 70/30 (or 80/20).\n"
    "- **Divergence** — connect price highs vs indicator highs; a disagreement is the headline signal.",
    "pane": "- **Zero-line crosses** — colour the area above zero green, below red; mark each cross.\n"
    "- **Histogram** — for *_hist columns, draw vertical bars from the zero line (rising/falling colour).\n"
    "- **Signal-line cross** — where a *_signal line is present, mark fast-crossing-signal events.\n"
    "- **Divergence** vs price for momentum-type readings.",
    "markers": "- **Cluster with context** — only highlight prints that occur at support/resistance or with a trend filter.\n"
    "- **Colour by direction** — green for bullish patterns, red for bearish.\n"
    "- **Tooltip** the pattern name + the bar's OHLC on hover.",
}

COMPANION = {
    "trend": "volume, plus a momentum oscillator (RSI or MACD) in a second pane.",
    "momentum": "the price chart above (for divergence) and a trend filter (SMA/ADX).",
    "volatility": "Bollinger %B or bandwidth, and a volume pane.",
    "volume": "the price chart and OBV/▲▼ coloured volume bars.",
    "statistics": "the raw price series it is computed from, for context.",
    "cycle": "price and a trend/▵cycle-mode flag.",
    "structure": "the price chart with horizontal support/resistance levels.",
    "price_transform": "candlesticks (it is an alternative price series).",
    "math_transform": "the source series it transforms.",
    "candles": "support/resistance levels and a trend filter to qualify the signal.",
    "utils": "the two series being compared (e.g. fast vs slow MA).",
    "relative": "the benchmark/index and the price chart.",
}


def render(spec) -> str:
    kind = classify(spec)
    what = _what(spec.name)
    aliases = ", ".join(spec.aliases) if spec.aliases else spec.name
    outs = ", ".join(f"`{c}`" for c in spec.outputs) if spec.outputs else "—"
    multi = len(spec.outputs) > 1
    flags = []
    if not spec.causal:
        flags.append("⚠️ **not causal** — forward-shifted; do not use the leading edge for live decisions")
    if spec.stateful:
        flags.append("path-dependent (its value depends on prior bars' state)")
    lines = [
        f"# `{spec.name}` — visualization ideas",
        "",
        f"> **{aliases}** · category **{spec.category}** · reads `{', '.join(spec.inputs)}` · outputs {outs}",
        "",
        f"**What it measures.** {what}",
        "",
    ]
    if flags:
        lines += ["> " + " · ".join(flags), ""]
    lines += ["## Where to draw it", "", PLACEMENT[kind], ""]
    lvl = _levels(spec)
    lines += ["## Scale & reference lines", ""]
    if kind in ("overlay", "band"):
        lines += ["Same **price scale** as the candles (no separate axis). " + (lvl or "") , ""]
    elif kind == "markers":
        lines += ["No vertical scale — the markers sit on the price candles at the firing bars.", ""]
    else:
        lines += [(lvl or "Auto-scale to the data; add a **zero line** if it oscillates around zero."), ""]
    lines += ["## Rendering each output", ""]
    for c in spec.outputs:
        if "hist" in c:
            lines.append(f"- `{c}` → **histogram** bars from the zero line (green rising / red falling).")
        elif "signal" in c:
            lines.append(f"- `{c}` → a thinner **signal line** over the main line; mark crossovers.")
        elif "dir" in c:
            lines.append(f"- `{c}` → **don't plot as a line** — use it to colour the main line/segments (up vs down).")
        elif any(k in c for k in ("upper", "lower", "_ub", "_lb", "band")):
            lines.append(f"- `{c}` → a **band edge**; shade between upper and lower.")
        elif "mid" in c:
            lines.append(f"- `{c}` → the **centre line**, drawn dashed.")
        else:
            lines.append(f"- `{c}` → the **main line**." if not multi else f"- `{c}` → a line.")
    lines += ["", "## Visual signals to highlight", "", SIGNALS[kind], ""]
    lines += ["## Sketch", "", "```", SKETCH[kind].rstrip("\n"), "```", ""]
    lines += ["## Pairs well with", "", COMPANION.get(spec.category, "the price chart."), ""]
    lines += ["---", "_Auto-generated by `scripts/build_graph_ideas.py` from the registry — ideas only, no plotting code._", ""]
    return "\n".join(lines)


def build() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    names = sorted(pyi.INDICATORS.names())
    by_cat: dict[str, list[str]] = {}
    for name in names:
        spec = pyi.INDICATORS.get(name).spec
        (OUT / f"{name}.md").write_text(render(spec))
        by_cat.setdefault(spec.category, []).append(name)
    # index
    idx = [
        "# Indicator visualization ideas",
        "",
        f"One Markdown file per indicator with **charting ideas only** (no plotting code): where to "
        f"draw it, what scale and reference lines to use, how to render each output, and which visual "
        f"signals to highlight. **{len(names)} indicators** across {len(by_cat)} categories. "
        "Auto-generated from the registry by `scripts/build_graph_ideas.py`.",
        "",
    ]
    for cat in CATEGORIES:
        if cat not in by_cat:
            continue
        idx.append(f"## {cat} ({len(by_cat[cat])})")
        idx.append("")
        idx.append(" · ".join(f"[`{n}`]({n}.md)" for n in sorted(by_cat[cat])))
        idx.append("")
    (OUT / "README.md").write_text("\n".join(idx))
    return len(names)


if __name__ == "__main__":
    n = build()
    print(f"wrote {n} graph-idea files + README to docs/graphs/")
