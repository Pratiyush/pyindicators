"""The auto-generated catalog must cover every registered indicator and stay in sync.

The drift test enforces the rule that ``docs/CATALOG.md`` is regenerated whenever an
indicator is added or changed:
``uv run python -c "from pyindicators.catalog import catalog_markdown;
open('docs/CATALOG.md','w').write(catalog_markdown())"``.
"""

from __future__ import annotations

from pathlib import Path

from pyindicators import INDICATORS
from pyindicators.catalog import catalog_markdown, catalog_rows

_CATALOG_PATH = Path(__file__).resolve().parents[2] / "docs" / "CATALOG.md"


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


def test_catalog_file_is_up_to_date():
    # Fails if docs/CATALOG.md wasn't regenerated after adding/changing an indicator.
    assert _CATALOG_PATH.exists(), "docs/CATALOG.md missing — regenerate it"
    assert _CATALOG_PATH.read_text() == catalog_markdown(), (
        "docs/CATALOG.md is stale — regenerate with "
        "`python -c \"from pyindicators.catalog import catalog_markdown; "
        "open('docs/CATALOG.md','w').write(catalog_markdown())\"`"
    )
