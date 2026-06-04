"""candles/ — candlestick-pattern recognition (TA-Lib ``CDL*`` compatible).

Every pattern composes :mod:`pyindicators.candles._candles`, which reproduces TA-Lib's
``CandleSettings`` averaging bit-exactly (see that module for the verified formula). Importing
this package registers each pattern's :class:`~pyindicators.core.Indicator` into
:data:`~pyindicators.core.INDICATORS`. Outputs are integer-valued (-100/0/100, with ±80 for
the partial engulfing/harami penetration score) matching ``talib.CDL*`` exactly.
"""

from __future__ import annotations

from .doji import Doji, doji
from .engulfing import Engulfing, engulfing
from .harami import Harami, harami
from .marubozu import Marubozu, marubozu
from .spinning_top import SpinningTop, spinning_top

__all__ = [
    "Doji",
    "doji",
    "Marubozu",
    "marubozu",
    "SpinningTop",
    "spinning_top",
    "Engulfing",
    "engulfing",
    "Harami",
    "harami",
]
