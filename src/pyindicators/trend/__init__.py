"""trend/ — moving averages and directional/trend systems."""

from __future__ import annotations

from .adx import ADX, directional_movement
from .apo import APO, apo
from .aroon import Aroon, aroon
from .dema import DEMA, dema
from .hma import HMA, hma
from .kama import KAMA, kama
from .kst import KST, kst
from .macd import MACD, macd
from .ppo import PPO, ppo
from .supertrend import Supertrend, supertrend
from .t3 import T3, t3
from .tema import TEMA, tema
from .trima import TRIMA, trima
from .trix import TRIX, trix
from .vortex import Vortex, vortex

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
    "Aroon", "aroon",
    "Vortex", "vortex",
    "KAMA", "kama",
    "Supertrend", "supertrend",
    "ADX", "directional_movement",
    "KST", "kst",
]
