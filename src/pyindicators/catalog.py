"""Indicator catalog metadata, derived from the registry.

Because every indicator's ``IndicatorSpec`` is the single source of truth, this catalog can
never drift from the code. :func:`catalog_rows` feeds the metadata columns of
``docs/TRACKING.md`` (via ``scripts/build_tracking.py``); :func:`catalog_markdown` renders the
same data as standalone Markdown if a category-grouped listing is ever needed.
"""

from __future__ import annotations

from .core import CATEGORIES, INDICATORS


def catalog_rows() -> list[dict]:
    """One metadata row per registered indicator (sorted by name)."""
    rows = []
    for name in INDICATORS.names():
        spec = INDICATORS.get(name).spec
        rows.append(
            {
                "name": spec.name,
                "category": spec.category,
                "inputs": spec.inputs,
                "outputs": spec.outputs,
                "aliases": spec.aliases,
                "references": spec.references,
            }
        )
    return rows


def catalog_markdown() -> str:
    """Render the full catalog as Markdown, grouped by category."""
    rows = catalog_rows()
    by_category: dict[str, list[dict]] = {}
    for row in rows:
        by_category.setdefault(row["category"], []).append(row)

    used = [c for c in CATEGORIES if c in by_category]
    lines = [
        "# pyindicators — indicator catalog",
        "",
        f"_Auto-generated from the registry metadata (do not edit by hand)._ "
        f"**{len(rows)} indicators** across {len(used)} categories.",
        "",
    ]
    for category in CATEGORIES:
        items = sorted(by_category.get(category, []), key=lambda r: r["name"])
        if not items:  # pragma: no cover - every category is now populated; guard kept for empties
            continue
        lines.append(f"## {category} ({len(items)})")
        lines.append("")
        lines.append("| id | outputs | inputs | aliases |")
        lines.append("|----|---------|--------|---------|")
        for row in items:
            lines.append(
                f"| `{row['name']}` | {', '.join(row['outputs'])} "
                f"| {', '.join(row['inputs'])} | {', '.join(row['aliases'])} |"
            )
        lines.append("")
    return "\n".join(lines)
