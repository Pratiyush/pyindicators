"""The registry-derived catalog metadata must cover every indicator.

``docs/CATALOG.md`` was retired — ``docs/TRACKING.md`` (built by ``scripts/build_tracking.py``)
is now the single source of truth and folds in the same metadata. ``pyindicators.catalog``
remains the API that feeds it, so these tests still guard that it stays complete and renderable.
"""

from __future__ import annotations

from pyindicators import INDICATORS
from pyindicators.catalog import catalog_markdown, catalog_rows


def test_catalog_rows_cover_all_indicators():
    rows = catalog_rows()
    assert len(rows) == len(INDICATORS)
    assert {r["name"] for r in rows} == set(INDICATORS.names())


def test_catalog_markdown_lists_every_indicator():
    md = catalog_markdown()
    assert md.startswith("# pyindicators")
    for name in INDICATORS.names():
        assert f"`{name}`" in md
    assert "## base" in md and "## momentum" in md  # at least these categories rendered
