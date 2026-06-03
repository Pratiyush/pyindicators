"""``IndicatorSpec`` — the typed, declarative description carried by every indicator.

This is the single source of truth for an indicator's identity and contract. It drives:
- registry keys (``spec.name``),
- input/output validation in the :class:`~pyindicators.core.indicator.Indicator` base,
- the parity-test mapping (which reference library to compare against),
- documentation generation / cross-linking to the 10-section ``.md`` spec.

Because it is ``frozen``, an indicator's declared contract cannot mutate at runtime.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .types import CATEGORIES, OHLCV_COLUMNS


class IndicatorSpec(BaseModel):
    """Declarative metadata for one indicator (see module docstring)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    #: Registered short id, e.g. ``"rsi"``. Lower snake_case.
    name: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    #: One of :data:`~pyindicators.core.types.CATEGORIES`.
    category: str
    #: Human-friendly alternative names (for docs / discovery).
    aliases: tuple[str, ...] = ()
    #: OHLCV columns the indicator reads (subset of ``OHLCV_COLUMNS``).
    inputs: tuple[str, ...]
    #: Output column names; ``compute`` returns exactly these, in this order.
    outputs: tuple[str, ...]
    #: Output column -> inclusive ``(low, high)`` bounds (e.g. RSI ``{"rsi": (0, 100)}``).
    bounds: dict[str, tuple[float, float]] = Field(default_factory=dict)
    #: Value at bar ``i`` depends only on rows ``<= i`` (no look-ahead). Almost always True.
    causal: bool = True
    #: True when seeding/smoothing matches TA-Lib (vs the pandas ``ewm`` convention).
    talib_compatible: bool = False
    #: True for path-dependent recurrences (Parabolic SAR, Supertrend, Heikin-Ashi, NVI/PVI).
    stateful: bool = False
    #: Canonical references / reference-library names used for parity tests.
    references: tuple[str, ...] = ()
    #: Path (relative to the repo) of the 10-section markdown spec, when one exists.
    doc: str | None = None

    @field_validator("category")
    @classmethod
    def _known_category(cls, v: str) -> str:
        if v not in CATEGORIES:
            raise ValueError(f"unknown category {v!r}; must be one of {CATEGORIES}")
        return v

    @field_validator("inputs")
    @classmethod
    def _inputs_are_ohlcv(cls, v: tuple[str, ...]) -> tuple[str, ...]:
        bad = [c for c in v if c not in OHLCV_COLUMNS]
        if bad:
            raise ValueError(f"inputs {bad} are not OHLCV columns {OHLCV_COLUMNS}")
        return v

    @field_validator("outputs")
    @classmethod
    def _outputs_unique_nonempty(cls, v: tuple[str, ...]) -> tuple[str, ...]:
        if not v:
            raise ValueError("outputs must be non-empty")
        if len(set(v)) != len(v):
            raise ValueError(f"output names must be unique: {v}")
        return v

    @model_validator(mode="after")
    def _bounds_reference_outputs(self) -> IndicatorSpec:
        bad = [k for k in self.bounds if k not in self.outputs]
        if bad:
            raise ValueError(f"bounds keys {bad} are not in outputs {self.outputs}")
        return self
