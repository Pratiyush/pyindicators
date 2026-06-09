"""Canonical timeframe tokens for the multi-timeframe layer.

:class:`Timeframe` is the single source of truth shared by ``resample_ohlcv`` /
``align_to_base`` and any downstream application. The string value doubles as a
data-partition key and, where applicable, a provider interval token, so the enum
compares equal to its token (``Timeframe.DAY == "1d"``).
"""

from __future__ import annotations

from enum import Enum


class Timeframe(str, Enum):
    """A bar interval, ordered coarse to fine (``MONTH`` highest, ``MIN1`` lowest)."""

    MONTH = "1mo"
    WEEK = "1wk"
    DAY = "1d"
    HOUR = "1h"
    MIN15 = "15m"
    MIN5 = "5m"
    MIN1 = "1m"

    @property
    def is_intraday(self) -> bool:
        """True for sub-daily bars (hour and finer)."""
        return self in {Timeframe.HOUR, Timeframe.MIN15, Timeframe.MIN5, Timeframe.MIN1}

    @property
    def pandas_rule(self) -> str:
        """Pandas ``resample`` rule string for aggregating *into* this timeframe."""
        return {
            Timeframe.MONTH: "MS",
            Timeframe.WEEK: "W-FRI",
            Timeframe.DAY: "1D",
            Timeframe.HOUR: "1h",
            Timeframe.MIN15: "15min",
            Timeframe.MIN5: "5min",
            Timeframe.MIN1: "1min",
        }[self]
