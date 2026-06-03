"""trend/ — moving averages and directional/trend systems."""

from __future__ import annotations

from .apo import APO, apo
from .dema import DEMA, dema
from .hma import HMA, hma
from .macd import MACD, macd
from .ppo import PPO, ppo
from .t3 import T3, t3
from .tema import TEMA, tema
from .trima import TRIMA, trima
from .trix import TRIX, trix

__all__ = [
    "MACD", "macd",
    "DEMA", "dema",
    "TEMA", "tema",
    "TRIMA", "trima",
    "T3", "t3",
    "HMA", "hma",
    "PPO", "ppo",
    "APO", "apo",
    "TRIX", "trix",
]
