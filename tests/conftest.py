"""Shared pytest configuration: a hypothesis profile with no per-example deadline (the
recursive indicators can be slow under coverage) and a modest example count."""

from __future__ import annotations

from hypothesis import settings

settings.register_profile("default", deadline=None, max_examples=50)
settings.load_profile("default")
