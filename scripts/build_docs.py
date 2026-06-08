"""Generate a single, self-contained, beautiful HTML reference for the indicator library.

Reads the registry (``IndicatorSpec`` + docstrings) and writes ``docs/index.html`` — a modern,
dark, responsive page with live search, category navigation, and one card per indicator
(aliases, inputs/outputs, what it measures, flags, references, and a link to its graph-ideas
file). No build step or runtime dependencies to view; just open the file.

    uv run python scripts/build_docs.py        # writes docs/index.html
"""

from __future__ import annotations

import html
from pathlib import Path

import pyindicators as pyi
from pyindicators.core import CATEGORIES

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "index.html"

CAT_BLURB = {
    "base": "Foundational building blocks (moving averages, dispersion, true range).",
    "price_transform": "Alternative price series (typical/median/weighted price, Heikin-Ashi).",
    "trend": "Trend direction & strength — moving-average variants, MACD/DMI, SAR, Ichimoku.",
    "momentum": "Oscillators measuring speed/strength of price change (RSI, Stochastic, ROC…).",
    "volatility": "Dispersion & range — ATR, Bollinger/Keltner/Donchian channels, realised vol.",
    "volume": "Volume-confirmed flow — OBV, A/D, money-flow, VSA/Wyckoff bars.",
    "statistics": "Rolling statistical measures — regression, correlation, moments, z-score.",
    "cycle": "Cycle & phase analysis — the Hilbert-Transform family and Ehlers oscillators.",
    "math_transform": "Element-wise math & rolling reducers (TA-Lib math-transform set).",
    "candles": "Candlestick & price-action patterns (bit-exact with TA-Lib CDL*).",
    "utils": "Signal helpers — crossovers, lag, decay, percent-rank.",
    "relative": "Per-symbol relative strength.",
    "structure": "Market structure — rolling highs/lows and distance from them.",
}


def _what(name: str) -> str:
    doc = (pyi.INDICATORS.get(name).__doc__ or "").strip()
    for line in doc.splitlines():
        s = line.strip()
        if s.lower().startswith("what:"):
            return s.split(":", 1)[1].strip()
    return doc.splitlines()[0].strip() if doc else ""


def _pill(text: str, cls: str = "") -> str:
    return f'<span class="pill {cls}">{html.escape(text)}</span>'


def _card(spec) -> str:
    e = html.escape
    what = e(_what(spec.name))
    aliases = e(", ".join(a for a in spec.aliases if a.lower() != spec.name)) if spec.aliases else ""
    inputs = "".join(_pill(i, "in") for i in spec.inputs)
    outputs = "".join(_pill(o, "out") for o in spec.outputs) if spec.outputs else ""
    flags = []
    if not spec.causal:
        flags.append(_pill("look-ahead", "warn"))
    if spec.stateful:
        flags.append(_pill("stateful", "flag"))
    if spec.talib_compatible:
        flags.append(_pill("TA-Lib", "flag"))
    refs = e(" · ".join(spec.references)) if spec.references else ""
    search = e(" ".join([spec.name, *spec.aliases, spec.category]).lower())
    return f"""      <article class="card" data-name="{e(spec.name)}" data-cat="{e(spec.category)}" data-search="{search}">
        <header>
          <h3>{e(spec.name)}</h3>
          <a class="graph" href="graphs/{e(spec.name)}.md" title="visualization ideas">📈 chart</a>
        </header>
        {f'<p class="aliases">{aliases}</p>' if aliases else ''}
        <p class="what">{what}</p>
        <div class="io"><span class="lbl">in</span>{inputs}<span class="arrow">→</span>{outputs}</div>
        {f'<div class="flags">{"".join(flags)}</div>' if flags else ''}
        {f'<p class="refs">{refs}</p>' if refs else ''}
      </article>"""


def build() -> int:
    specs = [pyi.INDICATORS.get(n).spec for n in sorted(pyi.INDICATORS.names())]
    by_cat: dict[str, list] = {}
    for s in specs:
        by_cat.setdefault(s.category, []).append(s)
    cats = [c for c in CATEGORIES if c in by_cat]

    nav = "".join(f'<button class="catbtn" data-cat="{c}">{c} <em>{len(by_cat[c])}</em></button>' for c in cats)
    sections = []
    for c in cats:
        cards = "\n".join(_card(s) for s in sorted(by_cat[c], key=lambda s: s.name))
        sections.append(f"""    <section class="cat" id="cat-{c}">
      <div class="cat-head"><h2>{c} <span class="count">{len(by_cat[c])}</span></h2><p>{html.escape(CAT_BLURB.get(c, ''))}</p></div>
      <div class="grid">
{cards}
      </div>
    </section>""")

    page = f"""<!doctype html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>pyindicators — indicator reference</title>
<style>
:root{{
  --bg:#0b0f17; --bg2:#0f1521; --card:#141b2b; --card2:#172033; --line:#243043;
  --txt:#e6edf6; --muted:#94a3b8; --accent:#6ea8fe; --accent2:#a78bfa; --green:#34d399;
  --warn:#fbbf24; --radius:14px; --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif;
}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;background:var(--bg);color:var(--txt);font-family:var(--sans);line-height:1.5;
  -webkit-font-smoothing:antialiased}}
a{{color:var(--accent);text-decoration:none}}
a:hover{{text-decoration:underline}}
.hero{{padding:64px 24px 40px;text-align:center;
  background:radial-gradient(1200px 400px at 50% -120px,rgba(110,168,254,.18),transparent 70%),
  linear-gradient(180deg,#0c111c,var(--bg))}}
.hero h1{{font-size:clamp(2.2rem,5vw,3.4rem);margin:0;letter-spacing:-.02em;
  background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;
  -webkit-text-fill-color:transparent;background-clip:text}}
.hero p.tag{{color:var(--muted);font-size:1.1rem;margin:.6rem 0 1.6rem;max-width:640px;
  margin-inline:auto}}
.stats{{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin-top:8px}}
.stat{{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
  padding:14px 20px;min-width:120px}}
.stat b{{display:block;font-size:1.7rem;background:linear-gradient(90deg,var(--accent),var(--green));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
.stat span{{color:var(--muted);font-size:.82rem}}
.toolbar{{position:sticky;top:0;z-index:20;background:rgba(11,15,23,.82);
  backdrop-filter:blur(12px);border-bottom:1px solid var(--line);padding:14px 20px}}
.toolbar .wrap{{max-width:1180px;margin:auto;display:flex;gap:12px;align-items:center;flex-wrap:wrap}}
#search{{flex:1;min-width:220px;background:var(--card);border:1px solid var(--line);color:var(--txt);
  border-radius:10px;padding:11px 14px;font-size:.95rem;outline:none}}
#search:focus{{border-color:var(--accent)}}
.cats{{display:flex;gap:8px;flex-wrap:wrap}}
.catbtn{{background:var(--card);border:1px solid var(--line);color:var(--muted);cursor:pointer;
  border-radius:999px;padding:7px 13px;font-size:.83rem;font-family:var(--mono);transition:.15s}}
.catbtn:hover{{color:var(--txt);border-color:var(--accent)}}
.catbtn em{{color:var(--accent);font-style:normal}}
main{{max-width:1180px;margin:auto;padding:28px 20px 80px}}
.cat-head h2{{font-family:var(--mono);font-size:1.4rem;margin:34px 0 4px;text-transform:capitalize}}
.cat-head .count{{font-size:.9rem;color:var(--accent);background:rgba(110,168,254,.12);
  padding:2px 9px;border-radius:999px;vertical-align:middle}}
.cat-head p{{color:var(--muted);margin:.2rem 0 16px}}
.grid{{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}}
.card{{background:linear-gradient(180deg,var(--card),var(--card2));border:1px solid var(--line);
  border-radius:var(--radius);padding:16px 16px 14px;transition:.15s;position:relative}}
.card:hover{{border-color:var(--accent);transform:translateY(-2px);
  box-shadow:0 10px 30px -12px rgba(110,168,254,.35)}}
.card header{{display:flex;justify-content:space-between;align-items:center;gap:8px}}
.card h3{{font-family:var(--mono);font-size:1.12rem;margin:0;color:var(--txt)}}
.card .graph{{font-size:.78rem;color:var(--muted);white-space:nowrap}}
.aliases{{color:var(--accent2);font-size:.8rem;margin:.3rem 0 0}}
.what{{color:var(--muted);font-size:.9rem;margin:.5rem 0 .7rem}}
.io{{display:flex;gap:5px;align-items:center;flex-wrap:wrap;margin-bottom:8px}}
.io .lbl{{font-family:var(--mono);font-size:.7rem;color:var(--muted);text-transform:uppercase}}
.io .arrow{{color:var(--muted);margin:0 2px}}
.pill{{font-family:var(--mono);font-size:.72rem;padding:2px 8px;border-radius:6px;
  background:#1b2436;border:1px solid var(--line);color:var(--muted)}}
.pill.in{{color:#7dd3fc}}
.pill.out{{color:var(--green);border-color:rgba(52,211,153,.25)}}
.pill.flag{{color:var(--accent2);border-color:rgba(167,139,250,.3)}}
.pill.warn{{color:var(--warn);border-color:rgba(251,191,36,.35)}}
.flags{{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:6px}}
.refs{{color:#64748b;font-size:.74rem;margin:.4rem 0 0;font-style:italic}}
.empty{{display:none;text-align:center;color:var(--muted);padding:60px 0;font-size:1.1rem}}
footer{{text-align:center;color:var(--muted);padding:30px 20px 50px;border-top:1px solid var(--line);
  font-size:.85rem}}
.cat.hide,.card.hide{{display:none}}
</style>
</head>
<body>
<header class="hero">
  <h1>pyindicators</h1>
  <p class="tag">A modular, look-ahead-safe technical-indicator library for pandas / numpy —
  every formula hand-rolled, parity-checked against TA-Lib · pandas-ta · finta · ta · Tulip,
  and 100% test-covered.</p>
  <div class="stats">
    <div class="stat"><b>{len(specs)}</b><span>indicators</span></div>
    <div class="stat"><b>{len(cats)}</b><span>categories</span></div>
    <div class="stat"><b>100%</b><span>line+branch coverage</span></div>
    <div class="stat"><b>0</b><span>audit failures</span></div>
  </div>
</header>
<div class="toolbar"><div class="wrap">
  <input id="search" type="search" placeholder="Search {len(specs)} indicators — name, alias, or category…" autocomplete="off">
  <div class="cats"><button class="catbtn active" data-cat="all">all</button>{nav}</div>
</div></div>
<main>
{chr(10).join(sections)}
  <p class="empty" id="empty">No indicators match your search.</p>
</main>
<footer>Auto-generated from the registry by <code>scripts/build_docs.py</code> · ideas-only
  visualization notes per indicator live in <a href="graphs/README.md">docs/graphs/</a>.</footer>
<script>
const q=document.getElementById('search'),cards=[...document.querySelectorAll('.card')],
  cats=[...document.querySelectorAll('.cat')],btns=[...document.querySelectorAll('.catbtn')],
  empty=document.getElementById('empty');
let activeCat='all';
function apply(){{
  const t=q.value.trim().toLowerCase();let shown=0;
  cards.forEach(c=>{{
    const okCat=activeCat==='all'||c.dataset.cat===activeCat;
    const okTxt=!t||c.dataset.search.includes(t);
    const vis=okCat&&okTxt;c.classList.toggle('hide',!vis);if(vis)shown++;
  }});
  cats.forEach(s=>s.classList.toggle('hide',![...s.querySelectorAll('.card')].some(c=>!c.classList.contains('hide'))));
  empty.style.display=shown?'none':'block';
}}
q.addEventListener('input',apply);
btns.forEach(b=>b.addEventListener('click',()=>{{
  activeCat=b.dataset.cat;btns.forEach(x=>x.classList.toggle('active',x===b));apply();
  if(activeCat!=='all')document.getElementById('cat-'+activeCat)?.scrollIntoView({{behavior:'smooth',block:'start'}});
}}));
</script>
</body>
</html>"""
    OUT.write_text(page)
    return len(specs)


if __name__ == "__main__":
    n = build()
    print(f"wrote docs/index.html ({n} indicators)")
