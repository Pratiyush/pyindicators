"""trend/ — moving averages and directional/trend systems."""

from __future__ import annotations

from .adx import ADX, directional_movement
from .adxr import ADXR, adxr
from .alma import ALMA, alma
from .apo import APO, apo
from .aroon import Aroon, aroon
from .chop import Choppiness, chop
from .dema import DEMA, dema
from .dpo import DPO, dpo
from .dx import DX, dx
from .fwma import FWMA, fwma
from .hma import HMA, hma
from .kama import KAMA, kama
from .kst import KST, kst
from .macd import MACD, macd
from .minus_di import MinusDI, minus_di
from .plus_di import PlusDI, plus_di
from .ppo import PPO, ppo
from .pwma import PWMA, pwma
from .qstick import QStick, qstick
from .sinwma import SINWMA, sinwma
from .sma_slope import SMASlope, sma_slope
from .supertrend import Supertrend, supertrend
from .swma import SWMA, swma
from .t3 import T3, t3
from .tema import TEMA, tema
from .trima import TRIMA, trima
from .trix import TRIX, trix
from .vhf import VHF, vhf
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
    "PlusDI", "plus_di",
    "MinusDI", "minus_di",
    "DX", "dx",
    "ADXR", "adxr",
    "Choppiness", "chop",
    "VHF", "vhf",
    "QStick", "qstick",
    "SMASlope", "sma_slope",
    "DPO", "dpo",
    "SWMA", "swma",
]
