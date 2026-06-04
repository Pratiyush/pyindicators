"""trend/ — moving averages and directional/trend systems."""

from __future__ import annotations

from .adx import ADX, directional_movement
from .alma import ALMA, alma
from .apo import APO, apo
from .aroon import Aroon, aroon
from .dema import DEMA, dema
from .fwma import FWMA, fwma
from .hma import HMA, hma
from .kama import KAMA, kama
from .kst import KST, kst
from .macd import MACD, macd
from .ppo import PPO, ppo
from .pwma import PWMA, pwma
from .sinwma import SINWMA, sinwma
from .supertrend import Supertrend, supertrend
from .t3 import T3, t3
from .tema import TEMA, tema
from .trima import TRIMA, trima
from .trix import TRIX, trix
from .vortex import Vortex, vortex
from .vwma import VWMA, vwma
from .zlma import ZLMA, zlma

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
    "VWMA", "vwma",
    "ZLMA", "zlma",
    "ALMA", "alma",
    "FWMA", "fwma",
    "SINWMA", "sinwma",
    "PWMA", "pwma",
]
