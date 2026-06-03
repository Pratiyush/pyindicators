"""The indicator registry.

Indicator classes self-register at import time via ``@INDICATORS.register``; the key is
``cls.spec.name``. Importing a category package (which imports its indicator modules) is
therefore all that's needed to make those indicators discoverable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .indicator import Indicator


class Registry:
    """A name -> class table for a kind of plugin (here: indicators)."""

    def __init__(self, kind: str = "indicator") -> None:
        self._kind = kind
        self._items: dict[str, type[Indicator]] = {}

    def register(self, cls: type[Indicator]) -> type[Indicator]:
        """Class decorator: register ``cls`` under ``cls.spec.name``."""
        name = cls.spec.name
        if name in self._items:
            raise ValueError(f"duplicate {self._kind} '{name}' already registered")
        self._items[name] = cls
        return cls

    def get(self, name: str) -> type[Indicator]:
        try:
            return self._items[name]
        except KeyError:
            raise KeyError(f"unknown {self._kind} '{name}'") from None

    def create(self, name: str, **params: object) -> Indicator:
        """Instantiate the registered indicator ``name`` with ``params``."""
        return self.get(name)(**params)

    def names(self) -> list[str]:
        return sorted(self._items)

    def all(self) -> dict[str, type[Indicator]]:
        return dict(self._items)

    def __contains__(self, name: object) -> bool:
        return name in self._items

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        return iter(self._items.values())


#: The global indicator registry.
INDICATORS = Registry("indicator")
