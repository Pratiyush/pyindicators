"""Timeframes and the canonical OHLCV column contract."""

from __future__ import annotations

from enum import Enum

#: The canonical OHLCV columns an indicator frame is expected to carry.
#: ``close`` is split/dividend-adjusted; ``close_raw`` is unadjusted; ``adj_factor`` = close/close_raw.
OHLCV_COLUMNS = ["ts", "open", "high", "low", "close", "close_raw", "volume", "adj_factor"]


class Timeframe(str, Enum):
    """Canonical timeframe tokens. The string value doubles as a partition key / interval token."""

    MONTH = "1mo"
    WEEK = "1wk"
    DAY = "1d"
    HOUR = "1h"
    MIN15 = "15m"
    MIN5 = "5m"
    MIN1 = "1m"

    @property
    def is_intraday(self) -> bool:
        return self in {Timeframe.HOUR, Timeframe.MIN15, Timeframe.MIN5, Timeframe.MIN1}

    @property
    def pandas_rule(self) -> str:
        """Pandas resample rule used when deriving higher timeframes."""
        return {
            Timeframe.MONTH: "MS",
            Timeframe.WEEK: "W-FRI",
            Timeframe.DAY: "1D",
            Timeframe.HOUR: "1h",
            Timeframe.MIN15: "15min",
            Timeframe.MIN5: "5min",
            Timeframe.MIN1: "1min",
        }[self]
