"""Indicator plugin registry.

Indicators register themselves into ``INDICATORS`` via a decorator, so a host
application looks them up by name and never imports concrete classes directly.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, TypeVar

T = TypeVar("T")


class Registry(Generic[T]):
    def __init__(self, kind: str) -> None:
        self.kind = kind
        self._items: dict[str, type[T]] = {}

    def register(self, name: str, *, override: bool = False) -> Callable[[type[T]], type[T]]:
        """Decorator: ``@INDICATORS.register("my_name")``."""

        def deco(cls: type[T]) -> type[T]:
            key = name.lower()
            if key in self._items and not override:
                raise ValueError(
                    f"{self.kind} '{name}' already registered "
                    f"({self._items[key].__module__}); pass override=True to replace."
                )
            self._items[key] = cls
            return cls

        return deco

    def get(self, name: str) -> type[T]:
        key = name.lower()
        if key not in self._items:
            raise KeyError(f"Unknown {self.kind} '{name}'. Known: {sorted(self._items)}")
        return self._items[key]

    def create(self, name: str, **params) -> T:
        """Look up and instantiate in one step."""
        return self.get(name)(**params)

    def all(self) -> dict[str, type[T]]:
        return dict(self._items)

    def names(self) -> list[str]:
        return sorted(self._items)

    def __contains__(self, name: str) -> bool:
        return name.lower() in self._items

    def __len__(self) -> int:
        return len(self._items)


#: The library-wide indicator registry. Importing ``pyindicators`` populates it.
INDICATORS: Registry = Registry("indicator")
