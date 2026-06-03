"""Hypothesis profiles for the indicator property suite."""

from __future__ import annotations

import os

from hypothesis import settings

settings.register_profile("dev", max_examples=20, deadline=None)
settings.register_profile("ci", max_examples=50, deadline=None)
settings.load_profile(os.environ.get("HYPOTHESIS_PROFILE", "dev"))
